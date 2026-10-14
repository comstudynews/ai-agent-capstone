import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = { title: "Operations Agent Cookbook", description: "Fictional training demo" };
export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="ko"><body>{children}</body></html>;
}
