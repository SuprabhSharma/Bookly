import { create } from "zustand";

const REFRESH_KEY = "marketplace_refresh_token";
export const useAuthStore = create((set) => ({
  accessToken: null,
  refreshToken: localStorage.getItem(REFRESH_KEY),
  user: null,
  setSession: ({ access_token, refresh_token, user }) => {
    if (refresh_token) localStorage.setItem(REFRESH_KEY, refresh_token);
    set({
      accessToken: access_token,
      refreshToken: refresh_token || localStorage.getItem(REFRESH_KEY),
      user,
    });
  },
  setAccessToken: (accessToken) => set({ accessToken }),
  setRefreshToken: (refreshToken) => {
    localStorage.setItem(REFRESH_KEY, refreshToken);
    set({ refreshToken });
  },
  setUser: (user) => set({ user }),
  logout: () => {
    localStorage.removeItem(REFRESH_KEY);
    set({ accessToken: null, refreshToken: null, user: null });
  },
}));
