"use client";

export default function TermsPage() {
  return (
    <div className="flex">
      <main className="">
        <h1 className="text-2xl font-bold mb-4">Terms and Conditions</h1>
        <p className="text-sm text-gray-600 mb-6">
          Last updated: June 25, 2025
        </p>

        <section className="mb-6">
          <h2 className="text-xl font-semibold mb-2">1. Acceptance of Terms</h2>
          <p>
            By accessing or using this website (the &quot;Service&quot;), you
            agree to be bound by these Terms and Conditions. If you do not agree
            with any part of these terms, you must stop using the Service
            immediately.
          </p>
        </section>

        <section className="mb-6">
          <h2 className="text-xl font-semibold mb-2">2. Changes to Terms</h2>
          <p>
            We reserve the right to modify these Terms at any time. We will
            notify you by updating the &quot;Last updated&quot; date at the top
            of this page. Your continued use of the Service after such changes
            constitutes acceptance of the new Terms.
          </p>
        </section>

        <section className="mb-6">
          <h2 className="text-xl font-semibold mb-2">3. Use of Service</h2>
          <p>
            You agree not to misuse the Service. Prohibited activities include
            hacking, distributing malware, or engaging in any illegal conduct.
          </p>
        </section>

        <section className="mb-6">
          <h2 className="text-xl font-semibold mb-2">
            4. Intellectual Property
          </h2>
          <p>
            All content, logos, and designs on this site are the property of
            [Your Company Name] or its licensors. You may view and download
            content only for personal, non-commercial use.
          </p>
        </section>

        <section className="mb-6">
          <h2 className="text-xl font-semibold mb-2">
            5. Limitation of Liability
          </h2>
          <p>
            In no event shall [Your Company Name] be liable for any indirect,
            incidental, or consequential damages arising out of your use of the
            Service.
          </p>
        </section>

        <section className="mb-6">
          <h2 className="text-xl font-semibold mb-2">6. Governing Law</h2>
          <p>
            These Terms shall be governed by the laws of [State/Country],
            without regard to conflict of law principles.
          </p>
        </section>

        <section>
          <h2 className="text-xl font-semibold mb-2">7. Contact Information</h2>
          <p>
            If you have any questions or concerns about these Terms, please
            contact us at{" "}
            <a href="mailto:contact@yourcompany.com" className="underline">
              contact@yourcompany.com
            </a>
            .
          </p>
        </section>
      </main>
    </div>
  );
}
