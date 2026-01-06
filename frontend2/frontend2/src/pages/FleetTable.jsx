import React, { useEffect, useMemo, useState } from "react";
// Adjust this import according to your project
import { fetchShap } from "../api";

// Utility: join classes
const cn = (...c) => c.filter(Boolean).join(" ");

// Status badge
function StatusBadge({ status }) {
    const palette =
        status === "On Time"
            ? "bg-emerald-100 text-emerald-800 border-emerald-200"
            : status === "Standby"
                ? "bg-sky-100 text-sky-800 border-sky-200"
                : "bg-rose-100 text-rose-800 border-rose-200";

    return (
        <span className={cn(
            "inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-medium",
            palette)} > {status}  </span>
    );
}

// Delay chip with thresholds
function DelayChip({ value }) {
    const v = typeof value === "number" ? value : null;
    const palette =
        v == null
            ? "bg-gray-100 text-gray-700 border-gray-200"
            : v <= 2
                ? "bg-emerald-50 text-emerald-700 border-emerald-200"
                : v <= 5
                    ? "bg-amber-50 text-amber-700 border-amber-200"
                    : "bg-rose-50 text-rose-700 border-rose-200";

    return (
        <span
            className={cn(
                "inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-medium",
                palette
            )}
        >
            {v == null ? "-" : v}
        </span>
    );
}

export default function FleetTable({ fleet = [] }) {
    const [shapData, setShapData] = useState({});
    const [hoverId, setHoverId] = useState(null);
    const [pos, setPos] = useState({ x: 0, y: 0 });

    // Fetch SHAP once per unique train_id
    useEffect(() => {
        let cancelled = false;
        const ids = Array.from(new Set(fleet.map((t) => t.train_id).filter(Boolean)));
        const toFetch = ids.filter((id) => shapData[id] === undefined);
        if (toFetch.length === 0) return;

        Promise.all(
            toFetch.map((id) =>
                fetchShap(id)
                    .then((data) => ({ id, data }))
                    .catch((error) => ({ id, error }))
            )
        ).then((results) => {
            if (cancelled) return;
            setShapData((prev) => {
                const next = { ...prev };
                results.forEach(({ id, data, error }) => {
                    if (!error) next[id] = data;
                    else console.error("SHAP fetch error:", id, error);
                });
                return next;
            });
        });

        return () => {
            cancelled = true;
        };
    }, [fleet, shapData]);

    const columns = useMemo(
        () => [
            { key: "train_id", label: "ID", className: "w-[80px]" },
            { key: "train_name", label: "Name" },
            { key: "day", label: "Day", className: "w-[90px]" },
            { key: "date", label: "Date", className: "w-[120px]" },
            { key: "scheduled_departure", label: "Departure", className: "w-[120px]" },
            { key: "scheduled_arrival", label: "Arrival", className: "w-[120px]" },
            { key: "status", label: "Status", className: "w-[120px]" },
            { key: "avg_delay_min", label: "Delay (min)", className: "w-[130px] text-right" },
        ],
        []
    );

    const renderTooltipContent = (id) => {
        const data = shapData[id];
        if (!data) {
            return (
                <div className="space-y-1">
                    <div className="h-3 w-36 animate-pulse rounded bg-gray-200 dark:bg-gray-700" />
                    <div className="h-3 w-28 animate-pulse rounded bg-gray-200 dark:bg-gray-700" />
                    <div className="h-3 w-32 animate-pulse rounded bg-gray-200 dark:bg-gray-700" />
                </div>
            );
        }
        // Sort features by absolute value (desc) and show top 8
        const entries = Object.entries(data).sort(
            (a, b) => Math.abs(b[1]) - Math.abs(a[1])
        );
        return (
            <div className="max-h-60 w-60 overflow-auto pr-1">
                {entries.slice(0, 8).map(([feature, value]) => (
                    <div
                        key={feature}
                        className="flex items-center justify-between text-xs text-gray-700 dark:text-gray-200"
                    >
                        <span className="mr-2 truncate">{feature}</span>
                        <span className="font-medium tabular-nums">
                            {Number.isFinite(+value) ? Number(value).toFixed(2) : value}
                        </span>
                    </div>
                ))}
                {entries.length > 8 && (
                    <div className="mt-1 text-[11px] text-gray-500">+{entries.length - 8} more</div>
                )}
            </div>
        );
    };

    return (
        <div className="overflow-x-auto rounded-xl border border-gray-200 bg-white shadow-sm dark:border-gray-800 dark:bg-gray-900">
            <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
                <thead className="bg-gray-50 dark:bg-gray-800">
                    <tr>
                        {columns.map((c) => (
                            <th
                                key={c.key}
                                className={cn(
                                    "px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-gray-600 dark:text-gray-300",
                                    c.className
                                )}
                            >
                                {c.label}
                            </th>
                        ))}
                    </tr>
                </thead>

                <tbody className="divide-y divide-gray-100 dark:divide-gray-800">
                    {fleet.map((t) => (
                        <tr
                            key={t.train_id}
                            className="group relative hover:bg-gray-50 dark:hover:bg-gray-800/60"
                            onMouseEnter={() => setHoverId(t.train_id)}
                            onMouseLeave={() => setHoverId((prev) => (prev === t.train_id ? null : prev))}
                            onMouseMove={(e) => setPos({ x: e.clientX + 14, y: e.clientY + 16 })}
                        >
                            <td className="px-4 py-3 text-sm font-medium text-gray-900 dark:text-gray-100">
                                {t.train_id}
                            </td>
                            <td className="px-4 py-3 text-sm text-gray-700 dark:text-gray-200">
                                {t.train_name}
                            </td>
                            <td className="px-4 py-3 text-sm text-gray-600 dark:text-gray-300">{t.day}</td>
                            <td className="px-4 py-3 text-sm text-gray-600 dark:text-gray-300">{t.date}</td>
                            <td className="px-4 py-3 text-sm text-gray-700 dark:text-gray-200">
                                {t.scheduled_departure}
                            </td>
                            <td className="px-4 py-3 text-sm text-gray-700 dark:text-gray-200">
                                {t.scheduled_arrival}
                            </td>
                            <td className="px-4 py-3">
                                <StatusBadge status={t.status} />
                            </td>
                            <td className="px-4 py-3 text-right">
                                <DelayChip value={t.avg_delay_min} />
                            </td>
                        </tr>
                    ))}
                    {fleet.length === 0 && (
                        <tr>
                            <td
                                colSpan={columns.length}
                                className="px-4 py-8 text-center text-sm text-gray-500 dark:text-gray-400"
                            >
                                No trains found
                            </td>
                        </tr>
                    )}
                </tbody>
            </table>

            {/* Floating SHAP tooltip (follows cursor) */}
            {hoverId && (
                <div
                    className="pointer-events-none fixed z-50 w-max max-w-xs rounded-lg border border-gray-200 bg-white p-3 text-xs shadow-lg backdrop-blur-sm
                     dark:border-gray-700 dark:bg-gray-900"
                    style={{ top: pos.y, left: pos.x }}
                >
                    <div className="mb-1 text-[11px] font-semibold uppercase tracking-wide text-gray-500 dark:text-gray-400">
                        SHAP features
                    </div>
                    {renderTooltipContent(hoverId)}
                </div>
            )}
        </div>
    );
}