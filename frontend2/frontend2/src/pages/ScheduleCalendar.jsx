import React, { useEffect, useMemo, useState } from "react";
import { Calendar, dateFnsLocalizer } from "react-big-calendar";
import { format, parse, startOfWeek, getDay } from "date-fns";
import enUS from "date-fns/locale/en-US";
import "react-big-calendar/lib/css/react-big-calendar.css";
import { fetchShap } from "../api";
// import { fetchShap } from "@/api";
// import { fetchShap } from "../../../../frontend/src/api";

// date-fns localizer (no moment)
const locales = { "en-US": enUS };
const localizer = dateFnsLocalizer({
    format,
    parse,
    startOfWeek,
    getDay,
    locales,
});

function formatShap(shap) {
    if (!shap || typeof shap !== "object") return "Loading SHAP...";
    return Object.entries(shap)
        .map(([f, v]) => `${f}: ${Number.isFinite(+v) ? Number(v).toFixed(2) : v}`)
        .join("\n");
}

const toDate = (val) => {
    if (!val) return null;
    if (val instanceof Date) return val;
    const d = new Date(val);
    return isNaN(d) ? null : d;
};

export default function ScheduleCalendar({
    assignments = [],
    initialDate = new Date(), // e.g., new Date(2025, 8, 26)
    today = new Date(),       // highlight "today"
}) {
    const [date, setDate] = useState(initialDate);
    const [shapData, setShapData] = useState({});

    // Fetch SHAP per unique trainset
    useEffect(() => {
        let cancelled = false;
        const uniqueTrainsets = Array.from(
            new Set(assignments.map((a) => a.trainset).filter(Boolean))
        );

        const toFetch = uniqueTrainsets.filter((ts) => shapData[ts] === undefined);
        if (toFetch.length === 0) return;

        Promise.all(
            toFetch.map((ts) =>
                fetchShap(ts)
                    .then((data) => ({ ts, data }))
                    .catch((error) => ({ ts, error }))
            )
        ).then((results) => {
            if (cancelled) return;
            setShapData((prev) => {
                const next = { ...prev };
                results.forEach(({ ts, data, error }) => {
                    if (!error) next[ts] = data;
                    else console.error("SHAP fetch error for", ts, error);
                });
                return next;
            });
        });

        return () => {
            cancelled = true;
        };
    }, [assignments, shapData]);

    const events = useMemo(() => {
        return assignments.map((a, i) => {
            const shap = shapData[a.trainset];
            const tooltip = formatShap(shap);

            // Prefer a.start/a.end if provided, else fallback to "now" + 1h
            const start =
                toDate(a.start) || toDate(a.date) || new Date();
            const end =
                toDate(a.end) ||
                new Date((toDate(a.start) || toDate(a.date) || new Date()).getTime() + 60 * 60 * 1000);

            return {
                id: i,
                title: `${a.trainset} - ${a.assignment}`,
                start,
                end,
                tooltip,
                // optional: add per-event color
                color: a.color, // e.g., "#3b82f6"
            };
        });
    }, [assignments, shapData]);

    return (
        <div className="mt-4 rounded-2xl border border-gray-200 bg-white p-6 shadow-sm">
            <h2 className="mb-3 text-xl font-semibold text-gray-800">AI Schedule Calendar</h2>

            <Calendar
                localizer={localizer}
                date={date}
                onNavigate={setDate}
                getNow={() => today}
                defaultView="month"
                views={["month", "week", "day"]}
                events={events}
                startAccessor="start"
                endAccessor="end"
                titleAccessor={(event) => event.title}
                tooltipAccessor={(event) => event.tooltip}
                style={{ height: 520 }}
                className="text-sm"
                messages={{
                    today: "Today",
                    previous: "Back",
                    next: "Next",
                    month: "Month",
                    week: "Week",
                    day: "Day",
                }}
                // Tailwind-like styling for events via inline styles (overrides RBC defaults)
                eventPropGetter={(event) => {
                    const base = {
                        backgroundColor: "rgba(59, 130, 246, 0.15)", // blue-500/15
                        color: "#1e40af", // blue-800
                        border: "1px solid #bfdbfe", // blue-200
                        borderRadius: "6px",
                        padding: "2px 6px",
                    };
                    // If event.color is provided, tint by that
                    if (event.color) {
                        return {
                            style: {
                                ...base,
                                backgroundColor: `${event.color}20`, // 12.5% alpha
                                border: `1px solid ${event.color}55`,
                                color: "#111827", // gray-900 for contrast
                            },
                        };
                    }
                    return { style: base };
                }}
                onSelectEvent={(e) => {
                    // Optional: click to see SHAP details
                    // eslint-disable-next-line no-alert
                    alert(`${e.title}\n\n${e.tooltip}`);
                }}
            />
        </div>
    );
}