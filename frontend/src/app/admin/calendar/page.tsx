"use client";

import { useEffect, useState } from "react";
import { useSession } from "next-auth/react";
import { useRouter } from "next/navigation";
import {
  blockTimeSlot,
  fetchCalendarAvailability,
  unblockTimeSlot,
} from "@/lib/admin-calendar";
import type { CalendarAvailability } from "@/types";

interface TimeSlot {
  hour: number;
  minute: number;
  label: string;
}

// Business hours: 8 AM to 6 PM
const TIME_SLOTS: TimeSlot[] = Array.from({ length: 21 }, (_, i) => {
  const hour = Math.floor(i / 2) + 8;
  const minute = (i % 2) * 30;
  return {
    hour,
    minute,
    label: `${hour.toString().padStart(2, "0")}:${minute.toString().padStart(2, "0")}`,
  };
});

const DAYS_OF_WEEK = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];

export default function AdminCalendarPage() {
  const { data: session, status } = useSession();
  const router = useRouter();

  const [view, setView] = useState<"month" | "week" | "day">("week");
  const [currentDate, setCurrentDate] = useState(new Date());
  const [blockedSlots, setBlockedSlots] = useState<CalendarAvailability[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedSlot, setSelectedSlot] = useState<CalendarAvailability | null>(null);
  const [blockReason, setBlockReason] = useState("");
  const [showBlockModal, setShowBlockModal] = useState(false);
  const [selectedDateTime, setSelectedDateTime] = useState<{
    date: string;
    timeSlot: string;
  } | null>(null);

  // Redirect if not authenticated or not admin
  useEffect(() => {
    if (status === "unauthenticated") {
      router.push("/auth/signin");
    } else if (status === "authenticated" && !session?.user?.isAdmin) {
      router.push("/");
    }
  }, [status, session, router]);

  // Fetch blocked slots when date range changes
  useEffect(() => {
    if (status === "authenticated" && session?.user?.isAdmin) {
      loadCalendarData();
    }
  }, [currentDate, view, status, session]);

  const loadCalendarData = async () => {
    if (!session?.accessToken) return;

    setLoading(true);
    setError(null);

    try {
      const { startDate, endDate } = getDateRange();
      const data = await fetchCalendarAvailability(
        startDate,
        endDate,
        false,
        session.accessToken
      );
      setBlockedSlots(data.items);
    } catch (err) {
      console.error("Error loading calendar:", err);
      setError("Failed to load calendar data");
    } finally {
      setLoading(false);
    }
  };

  const getDateRange = (): { startDate: string; endDate: string } => {
    const start = new Date(currentDate);
    const end = new Date(currentDate);

    if (view === "month") {
      start.setDate(1);
      end.setMonth(end.getMonth() + 1, 0);
    } else if (view === "week") {
      const day = start.getDay();
      start.setDate(start.getDate() - day);
      end.setDate(start.getDate() + 6);
    } else {
      // day view
      end.setDate(end.getDate());
    }

    return {
      startDate: formatDate(start),
      endDate: formatDate(end),
    };
  };

  const formatDate = (date: Date): string => {
    return date.toISOString().split("T")[0];
  };

  const isSlotBlocked = (date: Date, timeSlot: TimeSlot): CalendarAvailability | null => {
    const dateStr = formatDate(date);
    const timeStr = `${timeSlot.label}:00`;
    return (
      blockedSlots.find(
        (slot) => slot.date === dateStr && slot.timeSlot === timeStr
      ) || null
    );
  };

  const handleSlotClick = (date: Date, timeSlot: TimeSlot) => {
    const dateStr = formatDate(date);
    const timeStr = `${timeSlot.label}:00`;
    const blocked = isSlotBlocked(date, timeSlot);

    if (blocked) {
      setSelectedSlot(blocked);
    } else {
      setSelectedDateTime({ date: dateStr, timeSlot: timeStr });
      setBlockReason("");
      setShowBlockModal(true);
    }
  };

  const handleBlockSlot = async () => {
    if (!selectedDateTime || !session?.accessToken) return;

    setLoading(true);
    setError(null);

    try {
      await blockTimeSlot(
        {
          date: selectedDateTime.date,
          timeSlot: selectedDateTime.timeSlot,
          reason: blockReason || undefined,
        },
        session.accessToken
      );
      setShowBlockModal(false);
      setSelectedDateTime(null);
      setBlockReason("");
      await loadCalendarData();
    } catch (err: any) {
      console.error("Error blocking slot:", err);
      setError(err.response?.data?.detail || "Failed to block time slot");
    } finally {
      setLoading(false);
    }
  };

  const handleUnblockSlot = async (slotId: string) => {
    if (!session?.accessToken) return;

    setLoading(true);
    setError(null);

    try {
      await unblockTimeSlot(slotId, session.accessToken);
      setSelectedSlot(null);
      await loadCalendarData();
    } catch (err) {
      console.error("Error unblocking slot:", err);
      setError("Failed to unblock time slot");
    } finally {
      setLoading(false);
    }
  };

  const navigateDate = (direction: "prev" | "next") => {
    const newDate = new Date(currentDate);

    if (view === "month") {
      newDate.setMonth(newDate.getMonth() + (direction === "next" ? 1 : -1));
    } else if (view === "week") {
      newDate.setDate(newDate.getDate() + (direction === "next" ? 7 : -7));
    } else {
      newDate.setDate(newDate.getDate() + (direction === "next" ? 1 : -1));
    }

    setCurrentDate(newDate);
  };

  const goToToday = () => {
    setCurrentDate(new Date());
  };

  const getWeekDates = (): Date[] => {
    const dates: Date[] = [];
    const start = new Date(currentDate);
    const day = start.getDay();
    start.setDate(start.getDate() - day);

    for (let i = 0; i < 7; i++) {
      const date = new Date(start);
      date.setDate(start.getDate() + i);
      dates.push(date);
    }

    return dates;
  };

  const getDayDate = (): Date => {
    return new Date(currentDate);
  };

  const renderHeader = () => {
    let title = "";

    if (view === "month") {
      title = currentDate.toLocaleDateString("en-US", {
        month: "long",
        year: "numeric",
      });
    } else if (view === "week") {
      const weekDates = getWeekDates();
      const start = weekDates[0];
      const end = weekDates[6];
      title = `${start.toLocaleDateString("en-US", {
        month: "short",
        day: "numeric",
      })} - ${end.toLocaleDateString("en-US", {
        month: "short",
        day: "numeric",
        year: "numeric",
      })}`;
    } else {
      title = currentDate.toLocaleDateString("en-US", {
        weekday: "long",
        month: "long",
        day: "numeric",
        year: "numeric",
      });
    }

    return (
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-3xl font-bold">Calendar Management</h1>
          <p className="text-muted-foreground mt-1">
            Manage your booking availability and blocked time slots
          </p>
        </div>
      </div>
    );
  };

  const renderControls = () => (
    <div className="flex items-center justify-between mb-6 bg-card p-4 rounded-lg border">
      <div className="flex items-center gap-2">
        <button
          onClick={() => navigateDate("prev")}
          className="px-3 py-2 border rounded hover:bg-accent transition-colors"
          disabled={loading}
        >
          ← Previous
        </button>
        <button
          onClick={goToToday}
          className="px-4 py-2 border rounded hover:bg-accent transition-colors"
          disabled={loading}
        >
          Today
        </button>
        <button
          onClick={() => navigateDate("next")}
          className="px-3 py-2 border rounded hover:bg-accent transition-colors"
          disabled={loading}
        >
          Next →
        </button>
      </div>

      <div className="text-lg font-semibold">
        {view === "month"
          ? currentDate.toLocaleDateString("en-US", {
              month: "long",
              year: "numeric",
            })
          : view === "week"
          ? `${getWeekDates()[0].toLocaleDateString("en-US", {
              month: "short",
              day: "numeric",
            })} - ${getWeekDates()[6].toLocaleDateString("en-US", {
              month: "short",
              day: "numeric",
              year: "numeric",
            })}`
          : currentDate.toLocaleDateString("en-US", {
              weekday: "long",
              month: "long",
              day: "numeric",
              year: "numeric",
            })}
      </div>

      <div className="flex items-center gap-2">
        <button
          onClick={() => setView("day")}
          className={`px-4 py-2 rounded transition-colors ${
            view === "day"
              ? "bg-secondary text-secondary-foreground"
              : "border hover:bg-accent"
          }`}
          disabled={loading}
        >
          Day
        </button>
        <button
          onClick={() => setView("week")}
          className={`px-4 py-2 rounded transition-colors ${
            view === "week"
              ? "bg-secondary text-secondary-foreground"
              : "border hover:bg-accent"
          }`}
          disabled={loading}
        >
          Week
        </button>
        <button
          onClick={() => setView("month")}
          className={`px-4 py-2 rounded transition-colors ${
            view === "month"
              ? "bg-secondary text-secondary-foreground"
              : "border hover:bg-accent"
          }`}
          disabled={loading}
        >
          Month
        </button>
      </div>
    </div>
  );

  const renderWeekView = () => {
    const weekDates = getWeekDates();

    return (
      <div className="bg-card rounded-lg border overflow-hidden">
        <div className="grid grid-cols-8 border-b">
          <div className="p-3 border-r font-medium">Time</div>
          {weekDates.map((date, i) => (
            <div
              key={i}
              className={`p-3 text-center font-medium ${
                i < 6 ? "border-r" : ""
              } ${
                formatDate(date) === formatDate(new Date())
                  ? "bg-secondary/10 text-secondary"
                  : ""
              }`}
            >
              <div className="text-sm text-muted-foreground">
                {DAYS_OF_WEEK[date.getDay()]}
              </div>
              <div className="text-lg">{date.getDate()}</div>
            </div>
          ))}
        </div>

        <div className="max-h-[600px] overflow-y-auto">
          {TIME_SLOTS.map((timeSlot, slotIdx) => (
            <div key={slotIdx} className="grid grid-cols-8 border-b hover:bg-accent/5">
              <div className="p-2 border-r text-sm font-medium text-muted-foreground">
                {timeSlot.label}
              </div>
              {weekDates.map((date, dateIdx) => {
                const blocked = isSlotBlocked(date, timeSlot);
                const isToday = formatDate(date) === formatDate(new Date());

                return (
                  <button
                    key={dateIdx}
                    onClick={() => handleSlotClick(date, timeSlot)}
                    className={`p-2 text-xs border-r transition-colors relative group ${
                      blocked
                        ? "bg-red-100 hover:bg-red-200 dark:bg-red-900/30 dark:hover:bg-red-900/50"
                        : isToday
                        ? "hover:bg-secondary/20"
                        : "hover:bg-accent"
                    }`}
                    disabled={loading}
                  >
                    {blocked && (
                      <div className="flex items-center justify-center h-full">
                        <span className="text-red-600 dark:text-red-400 font-medium">
                          Blocked
                        </span>
                      </div>
                    )}
                    {blocked && (
                      <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 hidden group-hover:block z-10">
                        <div className="bg-popover text-popover-foreground text-xs rounded p-2 shadow-lg border whitespace-nowrap">
                          {blocked.reason || "No reason provided"}
                        </div>
                      </div>
                    )}
                  </button>
                );
              })}
            </div>
          ))}
        </div>
      </div>
    );
  };

  const renderDayView = () => {
    const date = getDayDate();

    return (
      <div className="bg-card rounded-lg border overflow-hidden">
        <div className="p-4 border-b font-medium">
          {date.toLocaleDateString("en-US", {
            weekday: "long",
            month: "long",
            day: "numeric",
            year: "numeric",
          })}
        </div>

        <div className="max-h-[600px] overflow-y-auto">
          {TIME_SLOTS.map((timeSlot, idx) => {
            const blocked = isSlotBlocked(date, timeSlot);

            return (
              <button
                key={idx}
                onClick={() => handleSlotClick(date, timeSlot)}
                className={`w-full p-4 border-b text-left transition-colors flex items-center justify-between group ${
                  blocked
                    ? "bg-red-100 hover:bg-red-200 dark:bg-red-900/30 dark:hover:bg-red-900/50"
                    : "hover:bg-accent"
                }`}
                disabled={loading}
              >
                <div className="flex items-center gap-4">
                  <span className="font-medium text-lg">{timeSlot.label}</span>
                  {blocked && (
                    <span className="px-3 py-1 bg-red-600 text-white text-sm rounded-full">
                      Blocked
                    </span>
                  )}
                </div>
                {blocked && (
                  <span className="text-sm text-muted-foreground">
                    {blocked.reason || "No reason provided"}
                  </span>
                )}
              </button>
            );
          })}
        </div>
      </div>
    );
  };

  const renderMonthView = () => {
    return (
      <div className="bg-card rounded-lg border p-6">
        <p className="text-center text-muted-foreground">
          Month view shows overview only. Switch to Week or Day view to manage time slots.
        </p>
        <div className="mt-6 grid grid-cols-7 gap-2">
          {DAYS_OF_WEEK.map((day) => (
            <div key={day} className="text-center font-medium p-2">
              {day}
            </div>
          ))}
          {Array.from({ length: new Date(currentDate.getFullYear(), currentDate.getMonth() + 1, 0).getDate() }, (_, i) => {
            const date = new Date(currentDate.getFullYear(), currentDate.getMonth(), i + 1);
            const dateStr = formatDate(date);
            const hasBlocked = blockedSlots.some((slot) => slot.date === dateStr);
            const isToday = formatDate(new Date()) === dateStr;

            return (
              <div
                key={i}
                className={`aspect-square border rounded p-2 text-center ${
                  hasBlocked ? "bg-red-100 dark:bg-red-900/30" : ""
                } ${isToday ? "border-secondary border-2" : ""}`}
              >
                <div className="font-medium">{i + 1}</div>
                {hasBlocked && (
                  <div className="text-xs text-red-600 dark:text-red-400 mt-1">
                    Blocked
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>
    );
  };

  if (status === "loading") {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-lg">Loading...</div>
      </div>
    );
  }

  if (!session?.user?.isAdmin) {
    return null;
  }

  return (
    <div className="min-h-screen bg-background p-6">
      <div className="max-w-7xl mx-auto">
        {renderHeader()}
        {renderControls()}

        {error && (
          <div className="mb-6 p-4 bg-destructive/10 text-destructive rounded-lg border border-destructive">
            {error}
          </div>
        )}

        {loading && (
          <div className="mb-6 p-4 bg-muted rounded-lg text-center">
            Loading calendar data...
          </div>
        )}

        {view === "week" && renderWeekView()}
        {view === "day" && renderDayView()}
        {view === "month" && renderMonthView()}

        {/* Block Slot Modal */}
        {showBlockModal && selectedDateTime && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
            <div className="bg-card p-6 rounded-lg max-w-md w-full mx-4 border">
              <h3 className="text-xl font-bold mb-4">Block Time Slot</h3>
              <p className="text-sm text-muted-foreground mb-4">
                Date: {selectedDateTime.date} at {selectedDateTime.timeSlot}
              </p>

              <div className="mb-4">
                <label className="block text-sm font-medium mb-2">
                  Reason (optional)
                </label>
                <textarea
                  value={blockReason}
                  onChange={(e) => setBlockReason(e.target.value)}
                  className="w-full p-2 border rounded focus:outline-none focus:ring-2 focus:ring-secondary"
                  rows={3}
                  placeholder="e.g., Personal appointment, Holiday, etc."
                />
              </div>

              <div className="flex gap-3">
                <button
                  onClick={handleBlockSlot}
                  disabled={loading}
                  className="flex-1 bg-red-600 text-white py-2 rounded hover:bg-red-700 transition-colors disabled:opacity-50"
                >
                  {loading ? "Blocking..." : "Block Slot"}
                </button>
                <button
                  onClick={() => {
                    setShowBlockModal(false);
                    setSelectedDateTime(null);
                    setBlockReason("");
                  }}
                  disabled={loading}
                  className="flex-1 border py-2 rounded hover:bg-accent transition-colors disabled:opacity-50"
                >
                  Cancel
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Slot Details Modal */}
        {selectedSlot && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
            <div className="bg-card p-6 rounded-lg max-w-md w-full mx-4 border">
              <h3 className="text-xl font-bold mb-4">Blocked Time Slot</h3>

              <div className="space-y-3 mb-6">
                <div>
                  <span className="text-sm font-medium text-muted-foreground">Date:</span>
                  <p className="text-lg">{selectedSlot.date}</p>
                </div>
                <div>
                  <span className="text-sm font-medium text-muted-foreground">Time:</span>
                  <p className="text-lg">{selectedSlot.timeSlot}</p>
                </div>
                <div>
                  <span className="text-sm font-medium text-muted-foreground">Reason:</span>
                  <p className="text-lg">{selectedSlot.reason || "No reason provided"}</p>
                </div>
                <div>
                  <span className="text-sm font-medium text-muted-foreground">Blocked at:</span>
                  <p className="text-sm">
                    {new Date(selectedSlot.createdAt).toLocaleString()}
                  </p>
                </div>
              </div>

              <div className="flex gap-3">
                <button
                  onClick={() => handleUnblockSlot(selectedSlot.id)}
                  disabled={loading}
                  className="flex-1 bg-green-600 text-white py-2 rounded hover:bg-green-700 transition-colors disabled:opacity-50"
                >
                  {loading ? "Unblocking..." : "Unblock Slot"}
                </button>
                <button
                  onClick={() => setSelectedSlot(null)}
                  disabled={loading}
                  className="flex-1 border py-2 rounded hover:bg-accent transition-colors disabled:opacity-50"
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
