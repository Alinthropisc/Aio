import { render, screen } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import { Button } from "../src/components/button";

describe("Button", () => {
  it("renders with default variant", () => {
    render(<Button>Click me</Button>);
    expect(screen.getByRole("button", { name: "Click me" })).toBeInTheDocument();
  });

  it("renders as child element when asChild is true", () => {
    render(
      <Button asChild>
        <a href="/test">Link</a>
      </Button>
    );
    expect(screen.getByRole("link", { name: "Link" })).toBeInTheDocument();
  });

  it("applies variant classes", () => {
    render(<Button variant="destructive">Delete</Button>);
    const btn = screen.getByRole("button", { name: "Delete" });
    expect(btn.className).toContain("bg-destructive");
  });

  it("is disabled when disabled prop is passed", () => {
    render(<Button disabled>Disabled</Button>);
    expect(screen.getByRole("button", { name: "Disabled" })).toBeDisabled();
  });
});
