// __tests__/LoginPage.test.tsx

import React, { use } from "react";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";

// 1. Mock next/navigation before your page import:
jest.mock("next/navigation", () => ({
  useRouter: jest.fn(),
}));

// 2. Mock your auth context hook:
jest.mock("@/context/AuthContext", () => ({
  __esModule: true,
  useAuth: jest.fn(),
}));

// 3. (Optional) stub out Link and Image so they become simple <a> and <img>
jest.mock("next/link", () => ({
  __esModule: true,
  default: ({ children, href, ...rest }: any) => (
    <a href={href} {...rest}>
      {children}
    </a>
  ),
}));
jest.mock("next/image", () => ({
  __esModule: true,
  default: (props: any) => <img {...props} />,
}));

import { useRouter } from "next/navigation";
import { useAuth } from "@/context/AuthContext";
import LoginPage from "@/app/login/page";

describe("LoginPage", () => {
  beforeEach(() => {
    // reset mocks
    (useRouter as jest.Mock).mockReset();
    (useAuth as jest.Mock).mockReset();
  });

  it("renders login form", () => {
    // Arrange: make the router & auth hooks return something minimal
    (useRouter as jest.Mock).mockReturnValue({ push: jest.fn() });
    (useAuth as jest.Mock).mockReturnValue({ login: jest.fn() });

    // Act
    render(<LoginPage />);

    // Assert
    expect(screen.getByLabelText(/username/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/password/i)).toBeInTheDocument();
  });

  it("calls login and redirects on submit", async () => {
    // Arrange: spy on login and push
    const loginMock = jest.fn(() => Promise.resolve());
    const pushMock = jest.fn();
    (useRouter as jest.Mock).mockReturnValue({ push: pushMock });
    (useAuth as jest.Mock).mockReturnValue({ login: loginMock });

    render(<LoginPage />);

    // Fill out and submit
    fireEvent.change(screen.getByLabelText(/username/i), {
      target: { value: "testuser" },
    });
    fireEvent.change(screen.getByLabelText(/password/i), {
      target: { value: "secret" },
    });
    fireEvent.click(screen.getByRole("button", { name: /login/i }));

    // Wait for the async handler to complete
    await waitFor(() => {
      expect(loginMock).toHaveBeenCalledWith("testuser", "secret");
      expect(pushMock).toHaveBeenCalledWith("/");
    });
  });
});
