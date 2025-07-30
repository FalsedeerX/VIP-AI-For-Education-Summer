/**
 * @jest-environment jsdom
 */
import React from "react";
import { render, screen } from "@testing-library/react";

// ── Mocks ──────────────────────────────────────────────────────────────────────
jest.mock("next/navigation", () => ({
  useParams: jest.fn(),
  useRouter: jest.fn(),
}));
jest.mock("@/app/chatscreen", () => ({
  __esModule: true,
  default: ({ chatId }: any) => <div>ChatScreen: {chatId}</div>,
}));
jest.mock("@/components/ui/sidebar", () => ({
  __esModule: true,
  default: () => <div>Sidebar</div>,
}));
jest.mock("@/context/AuthContext", () => ({
  __esModule: true,
  useAuth: jest.fn(),
}));

import { useParams, useRouter } from "next/navigation";
import { useAuth } from "@/context/AuthContext";
// Update the import path to the actual file location of the ChatPage component
import ChatPage from "@/app/chat/[chatId]/page";

describe("ChatPage", () => {
  const replaceMock = jest.fn();

  beforeEach(() => {
    (useParams as jest.Mock).mockReturnValue({ chatId: "123" });
    (useRouter as jest.Mock).mockReturnValue({ replace: replaceMock });
    replaceMock.mockReset();
    (useAuth as jest.Mock).mockReset();
  });

  it("redirects unauthenticated users to /login", () => {
    (useAuth as jest.Mock).mockReturnValue({ loading: false, userId: null });
    render(<ChatPage />);

    expect(replaceMock).toHaveBeenCalledWith("/login");
    // And nothing should render
    expect(screen.queryByText("Sidebar")).toBeNull();
    expect(screen.queryByText("ChatScreen")).toBeNull();
  });

  it("renders the sidebar and chat when authenticated", () => {
    (useAuth as jest.Mock).mockReturnValue({ loading: false, userId: "u1" });
    render(<ChatPage />);

    expect(screen.getByText("Sidebar")).toBeInTheDocument();
    expect(screen.getByText("ChatScreen: 123")).toBeInTheDocument();
    expect(replaceMock).not.toHaveBeenCalled();
  });
});
