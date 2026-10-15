import { create } from "zustand";

export const useAuthStore = create((set) => ({
  accessToken: null,
  user: null,
  isReady: false,
  setSession: ({ access_token, user }) => {
    set({ accessToken: access_token, user, isReady: true });
  },
  setAccessToken: (accessToken) => set({ accessToken }),
  setUser: (user) => set({ user }),
  setReady: () => set({ isReady: true }),
  logout: () => set({ accessToken: null, user: null, isReady: true }),
}));
