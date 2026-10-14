import uuid
from decimal import Decimal
from typing import Dict, List

from fastapi import HTTPException, status
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.db.models import Address, Cart, CartItem, Order, OrderItem, Product, SubOrder, Vendor
from src.errors import OrderNotFound

from .schemas import CheckoutRequest, OrderItemOut, OrderOut, SubOrderOut


class OrderService:
    async def checkout(self, user_id: uuid.UUID, data: CheckoutRequest, session: AsyncSession) -> OrderOut:
        """Atomic checkout: validate stock → decrement → snapshot → create Order/SubOrders → clear cart."""
        # 1. Fetch address
        addr_result = await session.exec(
            select(Address).where(Address.uid == data.address_id, Address.user_id == user_id)
        )
        addr = addr_result.first()
        if not addr:
            raise HTTPException(status_code=400, detail="Address not found")

        # 2. Fetch cart items
        cart_result = await session.exec(select(Cart).where(Cart.user_id == user_id))
        cart = cart_result.first()
        if not cart or not cart.items:
            raise HTTPException(status_code=400, detail="Cart is empty")

        # 3. Validate stock & group by vendor
        vendor_groups: Dict[uuid.UUID, List[CartItem]] = {}
        for item in cart.items:
            p_result = await session.exec(select(Product).where(Product.uid == item.product_id))
            product = p_result.first()
            if not product or product.status != "active":
                raise HTTPException(status_code=400, detail=f"Product unavailable: {item.product_id}")
            if product.stock < item.quantity:
                raise HTTPException(status_code=400, detail=f"Insufficient stock for: {product.title}")
            vendor_groups.setdefault(product.vendor_id, []).append(item)

        # 4. Mock online payment
        payment_status = "pending"
        if data.payment_method == "online_mock":
            payment_status = "paid"  # mock: always succeeds

        # 5. Decrement stock
        for item in cart.items:
            p_result = await session.exec(select(Product).where(Product.uid == item.product_id))
            product = p_result.first()
            product.stock -= item.quantity

        # 6. Build address snapshot
        addr_snapshot = {
            "name": addr.name, "phone": addr.phone,
            "line1": addr.line1, "line2": addr.line2,
            "city": addr.city, "state": addr.state, "pincode": addr.pincode,
        }

        # 7. Compute total
        total = Decimal("0.00")
        for items in vendor_groups.values():
            for item in items:
                p_result = await session.exec(select(Product).where(Product.uid == item.product_id))
                product = p_result.first()
                total += Decimal(str(product.price)) * item.quantity

        # 8. Create Order
        order = Order(
            user_id=user_id,
            address_snapshot=addr_snapshot,
            total=total,
            payment_method=data.payment_method,
            payment_status=payment_status,
            status="placed",
        )
        session.add(order)
        await session.flush()

        # 9. Create SubOrders + OrderItems
        sub_orders_out = []
        for vendor_id, items in vendor_groups.items():
            subtotal = Decimal("0.00")
            for item in items:
                p_result = await session.exec(select(Product).where(Product.uid == item.product_id))
                product = p_result.first()
                subtotal += Decimal(str(product.price)) * item.quantity

            sub = SubOrder(order_id=order.uid, vendor_id=vendor_id, subtotal=subtotal, status="placed")
            session.add(sub)
            await session.flush()

            order_items_out = []
            for item in items:
                p_result = await session.exec(select(Product).where(Product.uid == item.product_id))
                product = p_result.first()
                oi = OrderItem(
                    sub_order_id=sub.uid,
                    product_id=item.product_id,
                    title_snapshot=product.title,
                    price_snapshot=product.price,
                    quantity=item.quantity,
                )
                session.add(oi)
                order_items_out.append(OrderItemOut(
                    uid=oi.uid,
                    product_id=oi.product_id,
                    title_snapshot=oi.title_snapshot,
                    price_snapshot=oi.price_snapshot,
                    quantity=oi.quantity,
                    line_total=Decimal(str(oi.price_snapshot)) * oi.quantity,
                ))

            sub_orders_out.append(SubOrderOut(
                uid=sub.uid,
                vendor_id=sub.vendor_id,
                subtotal=sub.subtotal,
                status=sub.status,
                items=order_items_out,
            ))

        # 10. Clear cart
        for item in cart.items:
            await session.delete(item)

        await session.commit()
        await session.refresh(order)

        return OrderOut(
            uid=order.uid,
            total=order.total,
            payment_method=order.payment_method,
            payment_status=order.payment_status,
            status=order.status,
            address_snapshot=order.address_snapshot,
            sub_orders=sub_orders_out,
            created_at=order.created_at,
        )

    async def get_user_orders(self, user_id: uuid.UUID, session: AsyncSession) -> List[Order]:
        result = await session.exec(
            select(Order).where(Order.user_id == user_id).order_by(Order.created_at.desc())
        )
        return result.all()

    async def get_order(self, order_uid: uuid.UUID, user_id: uuid.UUID, session: AsyncSession):
        result = await session.exec(
            select(Order).where(Order.uid == order_uid, Order.user_id == user_id)
        )
        order = result.first()
        if not order:
            raise OrderNotFound()
        return order

    async def cancel_order(self, order_uid: uuid.UUID, user_id: uuid.UUID, session: AsyncSession):
        order = await self.get_order(order_uid, user_id, session)
        if order.status not in ("placed",):
            raise HTTPException(status_code=400, detail="Cannot cancel order in current state")
        order.status = "cancelled"
        for sub in order.sub_orders:
            sub.status = "cancelled"
        await session.commit()
        await session.refresh(order)
        return order

    async def update_suborder_status(self, sub_uid: uuid.UUID, vendor_id: uuid.UUID, new_status: str, session: AsyncSession):
        result = await session.exec(
            select(SubOrder).where(SubOrder.uid == sub_uid, SubOrder.vendor_id == vendor_id)
        )
        sub = result.first()
        if not sub:
            raise OrderNotFound()
        allowed = {"placed": ["confirmed"], "confirmed": ["shipped"], "shipped": ["delivered"]}
        if new_status not in allowed.get(sub.status, []):
            raise HTTPException(status_code=400, detail=f"Cannot move from {sub.status} to {new_status}")
        sub.status = new_status
        await session.commit()
        await session.refresh(sub)
        return sub
