import { notFound } from "next/navigation";
import MockClient from "./MockClient";

export default function MockPage() {
  if (process.env.NODE_ENV === "production") return notFound();

  return <MockClient />;
}
