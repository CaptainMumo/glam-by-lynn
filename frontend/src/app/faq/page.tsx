/**
 * FAQ Page
 * Frequently asked questions
 */

"use client";

import { Header } from "@/components/Header";
import { Footer } from "@/components/Footer";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

interface FAQ {
  category: string;
  questions: {
    question: string;
    answer: string;
  }[];
}

const faqs: FAQ[] = [
  {
    category: "Services & Booking",
    questions: [
      {
        question: "How far in advance should I book?",
        answer: "For bridal services, we recommend booking 3-6 months in advance. For other events, 2-4 weeks notice is preferred, though we can sometimes accommodate last-minute requests based on availability."
      },
      {
        question: "Do you offer trial sessions?",
        answer: "Yes! Trial sessions are included with all bridal packages and available as an add-on for other services. This allows us to perfect your look before your big day."
      },
      {
        question: "Do you provide on-location services?",
        answer: "Absolutely! We offer on-location services within a 50-mile radius. Travel fees may apply depending on distance and timing."
      },
      {
        question: "What is your cancellation policy?",
        answer: "We require 48 hours notice for cancellations or rescheduling. Deposits are non-refundable but can be transferred to a new date within 6 months."
      }
    ]
  },
  {
    category: "Pricing & Payments",
    questions: [
      {
        question: "What forms of payment do you accept?",
        answer: "We accept cash, credit/debit cards (Visa, Mastercard, American Express), and digital payment methods like Venmo and PayPal."
      },
      {
        question: "Is a deposit required?",
        answer: "Yes, a 50% deposit is required to secure your booking. The remaining balance is due on the day of service."
      },
      {
        question: "Are group bookings available?",
        answer: "Yes! We offer special rates for bridal parties and group bookings. Contact us for a custom quote."
      }
    ]
  },
  {
    category: "Makeup & Products",
    questions: [
      {
        question: "What brands do you use?",
        answer: "We use professional-grade makeup from leading brands including MAC, NARS, Charlotte Tilbury, and more. All products are high-quality and suitable for various skin types."
      },
      {
        question: "Do you work with sensitive skin?",
        answer: "Absolutely! We have experience with sensitive skin and various skin conditions. Please inform us of any allergies or sensitivities during booking."
      },
      {
        question: "Can I purchase the products you use?",
        answer: "Many of the products we use are available for purchase. We're happy to provide recommendations and can help you build your own makeup collection."
      },
      {
        question: "How long does makeup last?",
        answer: "Our professional makeup applications are designed to last 8-12 hours. We use setting sprays and long-wear formulas to ensure your look stays fresh."
      }
    ]
  },
  {
    category: "Classes & Learning",
    questions: [
      {
        question: "What skill level are the classes for?",
        answer: "We offer classes for all skill levels, from complete beginners to those looking to refine advanced techniques."
      },
      {
        question: "How long are the makeup classes?",
        answer: "Classes typically run 2-3 hours depending on the level and topic. Private lessons can be customized to your needs."
      },
      {
        question: "What should I bring to a class?",
        answer: "We provide all necessary makeup and tools for the class. Feel free to bring your own products if you'd like personalized guidance on items you own."
      }
    ]
  }
];

export default function FAQPage() {
  return (
    <div className="min-h-screen bg-background">
      <Header />

      {/* Hero Section */}
      <section className="border-b border-border bg-gradient-to-b from-background to-muted/20 px-4 py-16 md:py-24">
        <div className="container mx-auto">
          <div className="mx-auto max-w-3xl text-center">
            <Badge variant="secondary" className="mb-4">
              Help Center
            </Badge>
            <h1 className="mb-6 text-4xl font-bold tracking-tight md:text-5xl">
              Frequently Asked Questions
            </h1>
            <p className="text-lg text-muted-foreground">
              Find answers to common questions about our services, booking, and more
            </p>
          </div>
        </div>
      </section>

      <main className="container mx-auto px-4 py-16">
        <div className="mx-auto max-w-4xl space-y-12">
          {faqs.map((category, categoryIndex) => (
            <div key={categoryIndex}>
              <h2 className="mb-6 text-2xl font-bold">{category.category}</h2>
              <div className="space-y-4">
                {category.questions.map((faq, faqIndex) => (
                  <Card key={faqIndex}>
                    <CardHeader>
                      <CardTitle className="text-lg">{faq.question}</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <p className="text-muted-foreground">{faq.answer}</p>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </div>
          ))}

          {/* Contact Card */}
          <Card className="border-secondary/50 bg-muted/50">
            <CardContent className="p-8 text-center">
              <h3 className="mb-2 text-xl font-bold">
                Still have questions?
              </h3>
              <p className="mb-4 text-muted-foreground">
                We're here to help! Reach out and we'll get back to you as soon as possible.
              </p>
              <div className="text-sm text-muted-foreground">
                <p>Email: info@glambylynn.com</p>
                <p>Phone: (555) 123-4567</p>
              </div>
            </CardContent>
          </Card>
        </div>
      </main>

      <Footer />
    </div>
  );
}
