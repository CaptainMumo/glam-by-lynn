"""Analytics service for business intelligence."""
from datetime import datetime, timedelta
from decimal import Decimal
from typing import List, Tuple

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.booking import Booking
from app.models.order import Order, OrderItem
from app.models.product import Product
from app.models.service import ServicePackage
from app.models.user import User


def get_overview_stats(db: Session, start_date: datetime, end_date: datetime) -> dict:
    """
    Get overview statistics for the dashboard.

    Args:
        db: Database session
        start_date: Start date for the period
        end_date: End date for the period

    Returns:
        Dictionary with overview statistics
    """
    # Total revenue from orders in period
    total_revenue = (
        db.query(func.sum(Order.total_amount))
        .filter(
            Order.created_at >= start_date,
            Order.created_at <= end_date,
            Order.payment_confirmed == True,
        )
        .scalar()
        or Decimal(0)
    )

    # Total orders in period
    total_orders = (
        db.query(func.count(Order.id))
        .filter(Order.created_at >= start_date, Order.created_at <= end_date)
        .scalar()
        or 0
    )

    # Total bookings in period
    total_bookings = (
        db.query(func.count(Booking.id))
        .filter(Booking.created_at >= start_date, Booking.created_at <= end_date)
        .scalar()
        or 0
    )

    # Total products (all time)
    total_products = db.query(func.count(Product.id)).filter(Product.is_active == True).scalar() or 0

    # Total customers (all time)
    total_customers = db.query(func.count(User.id)).scalar() or 0

    # Pending orders
    pending_orders = (
        db.query(func.count(Order.id)).filter(Order.status == "pending").scalar() or 0
    )

    # Pending bookings
    pending_bookings = (
        db.query(func.count(Booking.id)).filter(Booking.status == "pending").scalar() or 0
    )

    # Calculate change percentages (compare with previous period)
    previous_start = start_date - (end_date - start_date)
    previous_end = start_date

    previous_revenue = (
        db.query(func.sum(Order.total_amount))
        .filter(
            Order.created_at >= previous_start,
            Order.created_at < previous_end,
            Order.payment_confirmed == True,
        )
        .scalar()
        or Decimal(0)
    )

    previous_orders = (
        db.query(func.count(Order.id))
        .filter(Order.created_at >= previous_start, Order.created_at < previous_end)
        .scalar()
        or 0
    )

    revenue_change = None
    if previous_revenue > 0:
        revenue_change = float(((total_revenue - previous_revenue) / previous_revenue) * 100)

    orders_change = None
    if previous_orders > 0:
        orders_change = ((total_orders - previous_orders) / previous_orders) * 100

    return {
        "totalRevenue": total_revenue,
        "totalOrders": total_orders,
        "totalBookings": total_bookings,
        "totalProducts": total_products,
        "totalCustomers": total_customers,
        "pendingOrders": pending_orders,
        "pendingBookings": pending_bookings,
        "revenueChangePercent": revenue_change,
        "ordersChangePercent": orders_change,
    }


def get_sales_analytics(
    db: Session, start_date: datetime, end_date: datetime, interval: str = "day"
) -> dict:
    """
    Get sales analytics with time series data.

    Args:
        db: Database session
        start_date: Start date for analysis
        end_date: End date for analysis
        interval: Time interval ('day', 'week', 'month')

    Returns:
        Dictionary with sales analytics
    """
    # Total revenue and orders
    total_revenue = (
        db.query(func.sum(Order.total_amount))
        .filter(
            Order.created_at >= start_date,
            Order.created_at <= end_date,
            Order.payment_confirmed == True,
        )
        .scalar()
        or Decimal(0)
    )

    total_orders = (
        db.query(func.count(Order.id))
        .filter(Order.created_at >= start_date, Order.created_at <= end_date)
        .scalar()
        or 0
    )

    average_order_value = total_revenue / total_orders if total_orders > 0 else Decimal(0)

    # Get data points grouped by date
    data_points = []

    if interval == "day":
        # Group by day
        current_date = start_date.date()
        end = end_date.date()

        while current_date <= end:
            day_start = datetime.combine(current_date, datetime.min.time())
            day_end = datetime.combine(current_date, datetime.max.time())

            day_revenue = (
                db.query(func.sum(Order.total_amount))
                .filter(
                    Order.created_at >= day_start,
                    Order.created_at <= day_end,
                    Order.payment_confirmed == True,
                )
                .scalar()
                or Decimal(0)
            )

            day_orders = (
                db.query(func.count(Order.id))
                .filter(Order.created_at >= day_start, Order.created_at <= day_end)
                .scalar()
                or 0
            )

            data_points.append({
                "date": current_date.isoformat(),
                "revenue": day_revenue,
                "orderCount": day_orders,
            })

            current_date += timedelta(days=1)

    return {
        "totalRevenue": total_revenue,
        "totalOrders": total_orders,
        "averageOrderValue": average_order_value,
        "dataPoints": data_points,
    }


def get_product_analytics(db: Session, start_date: datetime, end_date: datetime, limit: int = 10) -> dict:
    """
    Get product performance analytics.

    Args:
        db: Database session
        start_date: Start date for analysis
        end_date: End date for analysis
        limit: Number of top products to return

    Returns:
        Dictionary with product analytics
    """
    # Get top selling products
    top_products_query = (
        db.query(
            Product.id,
            Product.title,
            func.sum(OrderItem.quantity).label("total_sold"),
            func.sum(OrderItem.total_price).label("total_revenue"),
            Product.inventory_count,
        )
        .join(OrderItem, OrderItem.product_id == Product.id)
        .join(Order, OrderItem.order_id == Order.id)
        .filter(
            Order.created_at >= start_date,
            Order.created_at <= end_date,
            Order.payment_confirmed == True,
        )
        .group_by(Product.id)
        .order_by(func.sum(OrderItem.total_price).desc())
        .limit(limit)
        .all()
    )

    top_products = []
    for product in top_products_query:
        top_products.append({
            "productId": str(product.id),
            "productName": product.title,
            "totalSold": product.total_sold or 0,
            "totalRevenue": product.total_revenue or Decimal(0),
            "stockQuantity": product.inventory_count or 0,
        })

    # Total active products
    total_products = db.query(func.count(Product.id)).filter(Product.is_active == True).scalar() or 0

    # Low stock count (less than 10 items)
    low_stock_count = (
        db.query(func.count(Product.id))
        .filter(Product.is_active == True, Product.inventory_count < 10)
        .scalar()
        or 0
    )

    return {
        "topProducts": top_products,
        "totalProducts": total_products,
        "lowStockCount": low_stock_count,
    }


def get_booking_analytics(
    db: Session, start_date: datetime, end_date: datetime, interval: str = "day", limit: int = 5
) -> dict:
    """
    Get booking analytics with time series data.

    Args:
        db: Database session
        start_date: Start date for analysis
        end_date: End date for analysis
        interval: Time interval ('day', 'week', 'month')
        limit: Number of top services to return

    Returns:
        Dictionary with booking analytics
    """
    # Total bookings and revenue
    total_bookings = (
        db.query(func.count(Booking.id))
        .filter(Booking.created_at >= start_date, Booking.created_at <= end_date)
        .scalar()
        or 0
    )

    total_revenue = (
        db.query(func.sum(Booking.total_amount))
        .filter(
            Booking.created_at >= start_date,
            Booking.created_at <= end_date,
            Booking.status.in_(["confirmed", "completed"]),
        )
        .scalar()
        or Decimal(0)
    )

    # Booking status counts
    pending_bookings = (
        db.query(func.count(Booking.id))
        .filter(
            Booking.created_at >= start_date,
            Booking.created_at <= end_date,
            Booking.status == "pending",
        )
        .scalar()
        or 0
    )

    confirmed_bookings = (
        db.query(func.count(Booking.id))
        .filter(
            Booking.created_at >= start_date,
            Booking.created_at <= end_date,
            Booking.status == "confirmed",
        )
        .scalar()
        or 0
    )

    completed_bookings = (
        db.query(func.count(Booking.id))
        .filter(
            Booking.created_at >= start_date,
            Booking.created_at <= end_date,
            Booking.status == "completed",
        )
        .scalar()
        or 0
    )

    cancelled_bookings = (
        db.query(func.count(Booking.id))
        .filter(
            Booking.created_at >= start_date,
            Booking.created_at <= end_date,
            Booking.status == "cancelled",
        )
        .scalar()
        or 0
    )

    # Get data points grouped by date
    data_points = []

    if interval == "day":
        current_date = start_date.date()
        end = end_date.date()

        while current_date <= end:
            day_start = datetime.combine(current_date, datetime.min.time())
            day_end = datetime.combine(current_date, datetime.max.time())

            day_bookings = (
                db.query(func.count(Booking.id))
                .filter(Booking.created_at >= day_start, Booking.created_at <= day_end)
                .scalar()
                or 0
            )

            day_revenue = (
                db.query(func.sum(Booking.total_amount))
                .filter(
                    Booking.created_at >= day_start,
                    Booking.created_at <= day_end,
                    Booking.status.in_(["confirmed", "completed"]),
                )
                .scalar()
                or Decimal(0)
            )

            data_points.append({
                "date": current_date.isoformat(),
                "bookingCount": day_bookings,
                "revenue": day_revenue,
            })

            current_date += timedelta(days=1)

    # Top services by bookings
    top_services_query = (
        db.query(
            ServicePackage.id,
            ServicePackage.name,
            func.count(Booking.id).label("total_bookings"),
            func.sum(Booking.total_amount).label("total_revenue"),
        )
        .join(Booking, Booking.package_id == ServicePackage.id)
        .filter(
            Booking.created_at >= start_date,
            Booking.created_at <= end_date,
        )
        .group_by(ServicePackage.id)
        .order_by(func.count(Booking.id).desc())
        .limit(limit)
        .all()
    )

    top_services = []
    for service in top_services_query:
        top_services.append({
            "serviceId": str(service.id),
            "serviceName": service.name,
            "totalBookings": service.total_bookings or 0,
            "totalRevenue": service.total_revenue or Decimal(0),
        })

    return {
        "totalBookings": total_bookings,
        "totalRevenue": total_revenue,
        "pendingBookings": pending_bookings,
        "confirmedBookings": confirmed_bookings,
        "completedBookings": completed_bookings,
        "cancelledBookings": cancelled_bookings,
        "dataPoints": data_points,
        "topServices": top_services,
    }
