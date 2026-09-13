import { useEffect } from "react";
import OrganizationPanel from "../components/OrganizationPanel";

export default function OrganizationPage() {
  useEffect(() => {
    const timer = setTimeout(() => {
      const section = document.getElementById("organization-section");

      section?.scrollIntoView({
        behavior: "smooth",
        block: "start",
      });
    }, 100);

    return () => clearTimeout(timer);
  }, []);

  return <OrganizationPanel />;
}