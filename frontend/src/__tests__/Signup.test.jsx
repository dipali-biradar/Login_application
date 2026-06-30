import React from "react";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { BrowserRouter } from "react-router-dom";
import Signup from "../pages/Signup";
import { registerUser } from "../apis/authAPI";
import { matchIsValidTel } from "mui-tel-input";

// Mock the API
jest.mock("../apis/authAPI", () => ({
  registerUser: jest.fn(),
}));

// Mock the phone input component
jest.mock("mui-tel-input", () => ({
  MuiTelInput: ({ value, onChange }) => (
    <input
      data-testid="mobile-input"
      value={value}
      onChange={(e) => onChange(e.target.value)}
    />
  ),
  matchIsValidTel: jest.fn(),
}));

// Function to render Signup component
const renderSignup = () => {
  render(
    <BrowserRouter>
      <Signup />
    </BrowserRouter>
  );
};

describe("Signup Component", () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  // Test 1
  test("should display the signup form", () => {
    renderSignup();

    // Check if heading exists
    expect(screen.getByText("Create Account")).toBeInTheDocument();

    // Check if First Name textbox exists
    expect(screen.getByPlaceholderText("First Name")).toBeInTheDocument();

    // Check if Register button exists
    expect(
      screen.getByRole("button", { name: /register/i })
    ).toBeInTheDocument();
  });

  // Test 2
  test("should allow user to type in first name", () => {
    renderSignup();

    // Find the input
    const firstNameInput = screen.getByPlaceholderText("First Name");

    // Type into it
    fireEvent.change(firstNameInput, {
      target: { value: "Dipali" },
    });

    // Check entered value
    expect(firstNameInput.value).toBe("Dipali");
  });

  // Test 3
  test("should show error if mobile number is invalid", async () => {
    renderSignup();

    // Make phone validation fail
    matchIsValidTel.mockReturnValue(false);

    // Fill all required fields
    fireEvent.change(screen.getByPlaceholderText("First Name"), {
      target: { value: "Dipali" },
    });

    fireEvent.change(screen.getByPlaceholderText("Last Name"), {
      target: { value: "Biradar" },
    });

    fireEvent.change(screen.getByPlaceholderText("Email Address"), {
      target: { value: "dipali@test.com" },
    });

    fireEvent.change(screen.getByTestId("mobile-input"), {
      target: { value: "1234567890" },
    });

    fireEvent.change(screen.getByPlaceholderText("Password"), {
      target: { value: "password123" },
    });

    // Click Register
    fireEvent.click(
      screen.getByRole("button", { name: /register/i })
    );

    // Error message should appear
    expect(
      await screen.findByText("Please enter a valid mobile number")
    ).toBeInTheDocument();

    // API should not be called
    expect(registerUser).not.toHaveBeenCalled();
  });

  // Test 4
  test("should call register API when form is valid", async () => {
    renderSignup();

    // Make phone validation pass
    matchIsValidTel.mockReturnValue(true);

    // Mock successful API response
    registerUser.mockResolvedValue({
      data: {
        success: true,
      },
    });

    // Fill the form
    fireEvent.change(screen.getByPlaceholderText("First Name"), {
      target: { value: "Dipali" },
    });

    fireEvent.change(screen.getByPlaceholderText("Last Name"), {
      target: { value: "Biradar" },
    });

    fireEvent.change(screen.getByPlaceholderText("Email Address"), {
      target: { value: "dipali@test.com" },
    });

    fireEvent.change(screen.getByTestId("mobile-input"), {
      target: { value: "+911234567890" },
    });

    fireEvent.change(screen.getByPlaceholderText("Password"), {
      target: { value: "password123" },
    });

    // Submit form
    fireEvent.click(
      screen.getByRole("button", { name: /register/i })
    );

    // Wait until API is called
    await waitFor(() => {
      expect(registerUser).toHaveBeenCalled();
    });

    // Success message
    expect(
      screen.getByText(/Registration successful/i)
    ).toBeInTheDocument();
  });
});