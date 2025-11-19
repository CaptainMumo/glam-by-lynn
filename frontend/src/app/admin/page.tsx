/**
 * Admin Dashboard Homepage
 * Overview of key metrics and quick actions
 */

"use client";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import {
  Package,
  ShoppingBag,
  Calendar,
  Users,
  TrendingUp,
  TrendingDown,
  ArrowRight,
} from "lucide-react";
import Link from "next/link";

export default function AdminDashboard() {
  // Mock data - will be replaced with real API calls later
  const stats = [
    {
      title: "Total Products",
      value: "124",
      change: "+12%",
      trend: "up",
      icon: <Package className="h-4 w-4" />,
      href: "/admin/products",
    },
    {
      title: "Pending Orders",
      value: "23",
      change: "+5",
      trend: "up",
      icon: <ShoppingBag className="h-4 w-4" />,
      href: "/admin/orders",
    },
    {
      title: "Today's Bookings",
      value: "8",
      change: "+2",
      trend: "up",
      icon: <Calendar className="h-4 w-4" />,
      href: "/admin/bookings",
    },
    {
      title: "Total Customers",
      value: "1,234",
      change: "+18%",
      trend: "up",
      icon: <Users className="h-4 w-4" />,
      href: "/admin/users",
    },
  ];

  const recentActivity = [
    {
      id: 1,
      type: "order",
      message: "New order #1234 placed",
      time: "2 minutes ago",
    },
    {
      id: 2,
      type: "booking",
      message: "Booking confirmed for tomorrow",
      time: "15 minutes ago",
    },
    {
      id: 3,
      type: "product",
      message: "Product stock updated",
      time: "1 hour ago",
    },
  ];

  return (
    <div className="space-y-8">
      {/* Page Header */}
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
        <p className="text-muted-foreground">
          Welcome to your admin panel. Here's what's happening today.
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {stats.map((stat) => (
          <Card key={stat.title}>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">{stat.title}</CardTitle>
              <div className="rounded-full bg-secondary p-2">{stat.icon}</div>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stat.value}</div>
              <div className="flex items-center gap-1 text-xs text-muted-foreground">
                {stat.trend === "up" ? (
                  <TrendingUp className="h-3 w-3 text-green-600" />
                ) : (
                  <TrendingDown className="h-3 w-3 text-red-600" />
                )}
                <span className={stat.trend === "up" ? "text-green-600" : "text-red-600"}>
                  {stat.change}
                </span>
                <span>from last month</span>
              </div>
              <Link href={stat.href}>
                <Button variant="link" size="sm" className="mt-2 h-auto p-0">
                  View all
                  <ArrowRight className="ml-1 h-3 w-3" />
                </Button>
              </Link>
            </CardContent>
          </Card>
        ))}
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {/* Recent Activity */}
        <Card className="md:col-span-2">
          <CardHeader>
            <CardTitle>Recent Activity</CardTitle>
            <CardDescription>Latest updates from your store</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {recentActivity.map((activity) => (
                <div key={activity.id} className="flex items-start gap-4 border-b pb-4 last:border-0 last:pb-0">
                  <div className="flex h-10 w-10 items-center justify-center rounded-full bg-muted">
                    {activity.type === "order" && <ShoppingBag className="h-4 w-4" />}
                    {activity.type === "booking" && <Calendar className="h-4 w-4" />}
                    {activity.type === "product" && <Package className="h-4 w-4" />}
                  </div>
                  <div className="flex-1">
                    <p className="text-sm font-medium">{activity.message}</p>
                    <p className="text-xs text-muted-foreground">{activity.time}</p>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Quick Actions */}
        <Card>
          <CardHeader>
            <CardTitle>Quick Actions</CardTitle>
            <CardDescription>Common tasks</CardDescription>
          </CardHeader>
          <CardContent className="space-y-2">
            <Link href="/admin/products/new">
              <Button variant="outline" className="w-full justify-start">
                <Package className="mr-2 h-4 w-4" />
                Add Product
              </Button>
            </Link>
            <Link href="/admin/bookings">
              <Button variant="outline" className="w-full justify-start">
                <Calendar className="mr-2 h-4 w-4" />
                View Bookings
              </Button>
            </Link>
            <Link href="/admin/orders">
              <Button variant="outline" className="w-full justify-start">
                <ShoppingBag className="mr-2 h-4 w-4" />
                Manage Orders
              </Button>
            </Link>
            <Link href="/admin/calendar">
              <Button variant="outline" className="w-full justify-start">
                <Calendar className="mr-2 h-4 w-4" />
                Calendar
              </Button>
            </Link>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
