/**
 * @jest-environment jsdom
 */
import React from "react";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";

// ── Next.js & lib mocks ───────────────────────────────────────────────────────
jest.mock("next/navigation", () => ({ useRouter: jest.fn() }));
jest.mock("@/lib/api", () => ({ postJson: jest.fn() }));
jest.mock("@/context/AuthContext", () => ({
  __esModule: true,
  useAuth: jest.fn(),
}));

// ── Next.js UI mocks ──────────────────────────────────────────────────────────
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
  default: ({ priority, ...props }: any) => <img {...props} />,
}));

// ── Your UI-library mocks ─────────────────────────────────────────────────────
jest.mock("@/components/ui/input", () => ({
  __esModule: true,
  Input: (props: any) => <input {...props} />,
}));
jest.mock("@/components/ui/button", () => ({
  __esModule: true,
  Button: ({ children, ...props }: any) => (
    <button {...props}>{children}</button>
  ),
}));
jest.mock("@/components/ui/checkbox", () => ({
  __esModule: true,
  Checkbox: ({ checked, onCheckedChange, ...props }: any) => (
    <input
      type="checkbox"
      checked={checked}
      onChange={(e) => onCheckedChange?.(e.target.checked)}
      {...props}
    />
  ),
}));
jest.mock("@/components/ui/label", () => ({
  __esModule: true,
  Label: ({ htmlFor, children, ...props }: any) => (
    <label htmlFor={htmlFor} {...props}>
      {children}
    </label>
  ),
}));

import { useRouter } from "next/navigation";
import { postJson } from "@/lib/api";
import { useAuth } from "@/context/AuthContext";
import RegisterPage from "@/app/register/page";

describe("RegisterPage", () => {
  beforeEach(() => {
    (useRouter as jest.Mock).mockReset();
    (useAuth as jest.Mock).mockReset();
    (postJson as jest.Mock).mockReset();
  });

  it("renders all fields and buttons", () => {
    (useRouter as jest.Mock).mockReturnValue({ push: jest.fn() });
    (useAuth as jest.Mock).mockReturnValue({ login: jest.fn() });
    (postJson as jest.Mock).mockResolvedValue({ success: true });

    render(<RegisterPage />);
    expect(
      screen.getByRole("heading", { level: 2, name: /sign up/i })
    ).toBeInTheDocument();
    expect(screen.getByPlaceholderText(/Your username/i)).toBeInTheDocument();
    expect(screen.getByPlaceholderText(/you@example.com/i)).toBeInTheDocument();
    const pwInputs = screen.getAllByPlaceholderText("••••••••");
    expect(pwInputs).toHaveLength(2);
    expect(
      screen.getByRole("checkbox", { name: /I am an admin/i })
    ).toBeInTheDocument();
    expect(
      screen.getByRole("checkbox", { name: /Terms and Conditions/i })
    ).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /Sign Up/i })).toBeEnabled();
  });

  it("shows a password-mismatch error", async () => {
    (useRouter as jest.Mock).mockReturnValue({ push: jest.fn() });
    (useAuth as jest.Mock).mockReturnValue({ login: jest.fn() });
    (postJson as jest.Mock).mockResolvedValue({ success: true });

    const { container } = render(<RegisterPage />);
    const [password, confirm] = screen.getAllByPlaceholderText("••••••••");

    fireEvent.change(password, { target: { value: "foo" } });
    fireEvent.change(confirm, { target: { value: "bar" } });
    //fireEvent.click(screen.getByRole("button", { name: /Sign Up/i }));
    const form = container.querySelector("form");
    if (!form) throw new Error("Form element not found");
    fireEvent.submit(form);

    await waitFor(() => {
      expect(screen.getByText(/Passwords do not match/i)).toBeInTheDocument();
    });
  });
});
