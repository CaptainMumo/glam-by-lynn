"use client";

import { useState } from "react";
import Image from "next/image";
import { Header } from "@/components/Header";
import { Footer } from "@/components/Footer";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import {
  Sparkles,
  Scissors,
  Droplets,
  Truck,
  CheckCircle2,
  Users,
  MapPin,
  Mail,
  Phone,
  Loader2,
  Heart,
  Star,
  Clock,
  Award,
} from "lucide-react";
import { API_BASE_URL } from "@/config/api";

export default function Vision2026Page() {
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    phone: "",
    serviceInterest: "",
    message: "",
  });
  const [submitting, setSubmitting] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    setError("");

    try {
      // For now, just simulate submission
      // In production, this would call an API endpoint to save interest registrations
      await new Promise(resolve => setTimeout(resolve, 1500));

      setSuccess(true);
      setFormData({
        name: "",
        email: "",
        phone: "",
        serviceInterest: "",
        message: "",
      });

      setTimeout(() => setSuccess(false), 5000);
    } catch (err) {
      setError("Failed to submit your interest. Please try again.");
    } finally {
      setSubmitting(false);
    }
  };

  const services = [
    {
      icon: Sparkles,
      title: "Full-Service Salon",
      description: "Comprehensive hair care, styling, and treatments in a luxurious setting",
      features: [
        "Professional hair cutting and styling",
        "Color treatments and highlights",
        "Hair treatments and conditioning",
        "Blowouts and special occasion styling",
        "Bridal and event packages",
      ],
      image: "/placeholder-salon.jpg",
    },
    {
      icon: Scissors,
      title: "Modern Barbershop",
      description: "Premium grooming services for the modern gentleman",
      features: [
        "Classic and contemporary haircuts",
        "Hot towel shaves and beard grooming",
        "Hair and scalp treatments",
        "Grooming consultations",
        "Membership packages available",
      ],
      image: "/placeholder-barber.jpg",
    },
    {
      icon: Droplets,
      title: "Wellness Spa",
      description: "Rejuvenating treatments for complete mind and body wellness",
      features: [
        "Facials and skincare treatments",
        "Body massages and therapies",
        "Manicures and pedicures",
        "Waxing and threading services",
        "Couples spa packages",
      ],
      image: "/placeholder-spa.jpg",
    },
    {
      icon: Truck,
      title: "Mobile Beauty Van",
      description: "Bringing premium beauty services directly to you",
      features: [
        "On-location makeup services",
        "Mobile hair styling",
        "Event and wedding services",
        "Corporate wellness programs",
        "Serving Nairobi and Kitui regions",
      ],
      image: "/placeholder-van.jpg",
    },
  ];

  const benefits = [
    {
      icon: Award,
      title: "Expert Team",
      description: "Certified professionals with years of experience in beauty and wellness",
    },
    {
      icon: Star,
      title: "Premium Products",
      description: "Only the finest, professional-grade products for exceptional results",
    },
    {
      icon: Clock,
      title: "Flexible Hours",
      description: "Extended hours and weekend availability to fit your schedule",
    },
    {
      icon: MapPin,
      title: "Multiple Locations",
      description: "Conveniently located in Nairobi and Kitui, with mobile services",
    },
    {
      icon: Users,
      title: "Personalized Service",
      description: "Tailored treatments and consultations for your unique needs",
    },
    {
      icon: Heart,
      title: "Client-Focused",
      description: "Your satisfaction and comfort are our top priorities",
    },
  ];

  return (
    <div className="min-h-screen bg-background">
      <Header />

      {/* Hero Section */}
      <section className="relative overflow-hidden bg-gradient-to-br from-background via-secondary/5 to-background py-20 md:py-32">
        <div className="container mx-auto px-4">
          <div className="mx-auto max-w-4xl text-center">
            <Badge className="mb-6 text-base" variant="secondary">
              Coming 2026
            </Badge>
            <h1 className="mb-6 text-4xl font-bold tracking-tight md:text-6xl">
              Our <span className="text-secondary">Vision</span> for Tomorrow
            </h1>
            <p className="mb-8 text-lg text-muted-foreground md:text-xl">
              Building on our foundation of excellence in makeup artistry and beauty products,
              we're expanding to offer a complete beauty and wellness destination. From premium salon
              services to rejuvenating spa treatments, we're bringing world-class experiences to
              Nairobi and Kitui.
            </p>
            <div className="flex flex-col gap-4 sm:flex-row sm:justify-center">
              <Button size="lg" asChild>
                <a href="#interest-form">
                  Register Your Interest
                  <Sparkles className="ml-2 h-5 w-5" />
                </a>
              </Button>
              <Button size="lg" variant="outline" asChild>
                <a href="#services">Explore Services</a>
              </Button>
            </div>
          </div>
        </div>

        {/* Decorative elements */}
        <div className="absolute -left-4 top-1/4 h-72 w-72 rounded-full bg-secondary/10 blur-3xl" />
        <div className="absolute -right-4 bottom-1/4 h-96 w-96 rounded-full bg-secondary/10 blur-3xl" />
      </section>

      {/* Vision Statement */}
      <section className="py-16 md:py-24">
        <div className="container mx-auto px-4">
          <Card className="border-secondary/20 bg-gradient-to-br from-background to-secondary/5">
            <CardContent className="p-8 md:p-12">
              <div className="mx-auto max-w-3xl text-center">
                <Sparkles className="mx-auto mb-6 h-12 w-12 text-secondary" />
                <h2 className="mb-6 text-3xl font-bold md:text-4xl">
                  A Complete Beauty Ecosystem
                </h2>
                <p className="mb-6 text-lg text-muted-foreground">
                  By 2026, Glam by Lynn will be East Africa's premier destination for comprehensive
                  beauty and wellness services. We're creating spaces where artistry meets technology,
                  tradition meets innovation, and every client experiences transformation.
                </p>
                <p className="text-lg font-medium text-secondary">
                  "Where every visit is an experience, and every experience is unforgettable."
                </p>
              </div>
            </CardContent>
          </Card>
        </div>
      </section>

      {/* Services Section */}
      <section id="services" className="bg-muted/30 py-16 md:py-24">
        <div className="container mx-auto px-4">
          <div className="mb-12 text-center">
            <h2 className="mb-4 text-3xl font-bold md:text-4xl">
              Our <span className="text-secondary">2026</span> Service Offerings
            </h2>
            <p className="mx-auto max-w-2xl text-lg text-muted-foreground">
              Four distinct service categories designed to meet all your beauty and wellness needs
            </p>
          </div>

          <div className="grid gap-8 md:grid-cols-2">
            {services.map((service, index) => {
              const Icon = service.icon;
              return (
                <Card key={index} className="overflow-hidden transition-shadow hover:shadow-lg">
                  <div className="relative h-48 bg-muted">
                    {/* Placeholder for service images */}
                    <div className="flex h-full items-center justify-center bg-gradient-to-br from-secondary/20 to-secondary/5">
                      <Icon className="h-20 w-20 text-secondary/40" />
                    </div>
                  </div>
                  <CardHeader>
                    <div className="mb-2 flex items-center gap-2">
                      <Icon className="h-6 w-6 text-secondary" />
                      <CardTitle>{service.title}</CardTitle>
                    </div>
                    <CardDescription className="text-base">
                      {service.description}
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <ul className="space-y-2">
                      {service.features.map((feature, idx) => (
                        <li key={idx} className="flex items-start gap-2">
                          <CheckCircle2 className="mt-0.5 h-5 w-5 flex-shrink-0 text-secondary" />
                          <span className="text-sm text-muted-foreground">{feature}</span>
                        </li>
                      ))}
                    </ul>
                  </CardContent>
                </Card>
              );
            })}
          </div>
        </div>
      </section>

      {/* Benefits & Differentiators */}
      <section className="py-16 md:py-24">
        <div className="container mx-auto px-4">
          <div className="mb-12 text-center">
            <h2 className="mb-4 text-3xl font-bold md:text-4xl">
              Why Choose <span className="text-secondary">Glam by Lynn</span>
            </h2>
            <p className="mx-auto max-w-2xl text-lg text-muted-foreground">
              Our commitment to excellence sets us apart in the beauty and wellness industry
            </p>
          </div>

          <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {benefits.map((benefit, index) => {
              const Icon = benefit.icon;
              return (
                <Card key={index} className="border-secondary/10">
                  <CardContent className="pt-6">
                    <Icon className="mb-4 h-10 w-10 text-secondary" />
                    <h3 className="mb-2 text-xl font-semibold">{benefit.title}</h3>
                    <p className="text-muted-foreground">{benefit.description}</p>
                  </CardContent>
                </Card>
              );
            })}
          </div>
        </div>
      </section>

      {/* Target Market Messaging */}
      <section className="bg-secondary/5 py-16 md:py-24">
        <div className="container mx-auto px-4">
          <div className="mx-auto max-w-4xl">
            <div className="mb-12 text-center">
              <h2 className="mb-4 text-3xl font-bold md:text-4xl">
                Designed for <span className="text-secondary">You</span>
              </h2>
            </div>

            <div className="grid gap-8 md:grid-cols-3">
              <Card>
                <CardHeader>
                  <CardTitle className="text-xl">Busy Professionals</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-muted-foreground">
                    Flexible scheduling, express services, and mobile options that fit your lifestyle.
                    Look your best without compromising your schedule.
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="text-xl">Brides & Events</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-muted-foreground">
                    Comprehensive packages for your special day. From trials to the big day,
                    we ensure you look absolutely stunning.
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="text-xl">Wellness Seekers</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-muted-foreground">
                    Holistic treatments that nurture body and mind. Experience true relaxation
                    and rejuvenation in our spa facilities.
                  </p>
                </CardContent>
              </Card>
            </div>
          </div>
        </div>
      </section>

      {/* Interest Registration Form */}
      <section id="interest-form" className="py-16 md:py-24">
        <div className="container mx-auto px-4">
          <div className="mx-auto max-w-2xl">
            <div className="mb-8 text-center">
              <h2 className="mb-4 text-3xl font-bold md:text-4xl">
                Be the First to Know
              </h2>
              <p className="text-lg text-muted-foreground">
                Register your interest and receive exclusive updates on our 2026 launch,
                including early bird discounts and special offers.
              </p>
            </div>

            {success && (
              <div className="mb-6 rounded-md border border-green-200 bg-green-50 px-4 py-3">
                <div className="flex items-center gap-2 text-green-800">
                  <CheckCircle2 className="h-5 w-5" />
                  <span className="font-medium">Thank you for your interest!</span>
                </div>
                <p className="mt-1 text-sm text-green-700">
                  We'll keep you updated on our 2026 launch and send you exclusive early access offers.
                </p>
              </div>
            )}

            {error && (
              <div className="mb-6 rounded-md border border-red-200 bg-red-50 px-4 py-3 text-red-800">
                {error}
              </div>
            )}

            <Card>
              <CardContent className="pt-6">
                <form onSubmit={handleSubmit} className="space-y-6">
                  <div>
                    <Label htmlFor="name">Full Name *</Label>
                    <Input
                      id="name"
                      value={formData.name}
                      onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                      required
                      placeholder="Your name"
                    />
                  </div>

                  <div>
                    <Label htmlFor="email">Email Address *</Label>
                    <div className="relative">
                      <Mail className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                      <Input
                        id="email"
                        type="email"
                        value={formData.email}
                        onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                        required
                        placeholder="your@email.com"
                        className="pl-10"
                      />
                    </div>
                  </div>

                  <div>
                    <Label htmlFor="phone">Phone Number</Label>
                    <div className="relative">
                      <Phone className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                      <Input
                        id="phone"
                        type="tel"
                        value={formData.phone}
                        onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                        placeholder="+254..."
                        className="pl-10"
                      />
                    </div>
                  </div>

                  <div>
                    <Label htmlFor="serviceInterest">Service Interest</Label>
                    <Input
                      id="serviceInterest"
                      value={formData.serviceInterest}
                      onChange={(e) => setFormData({ ...formData, serviceInterest: e.target.value })}
                      placeholder="e.g., Salon, Spa, Barbershop, Mobile Services"
                    />
                  </div>

                  <div>
                    <Label htmlFor="message">Message (Optional)</Label>
                    <Textarea
                      id="message"
                      value={formData.message}
                      onChange={(e) => setFormData({ ...formData, message: e.target.value })}
                      placeholder="Tell us what excites you most about our 2026 vision..."
                      rows={4}
                    />
                  </div>

                  <Button
                    type="submit"
                    size="lg"
                    className="w-full"
                    disabled={submitting}
                  >
                    {submitting ? (
                      <>
                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                        Submitting...
                      </>
                    ) : (
                      <>
                        Register Your Interest
                        <Sparkles className="ml-2 h-4 w-4" />
                      </>
                    )}
                  </Button>

                  <p className="text-center text-sm text-muted-foreground">
                    By submitting, you agree to receive updates about our 2026 launch.
                    You can unsubscribe at any time.
                  </p>
                </form>
              </CardContent>
            </Card>
          </div>
        </div>
      </section>

      <Footer />
    </div>
  );
}
