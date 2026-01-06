// src/components/MaintenanceCards.jsx

export default function MaintenanceCards({ fleet = [] }) {
    const totalJobs = fleet.reduce((acc, t) => acc + (t?.job_cards_open ?? 0), 0);
    const cleaningNeeded = fleet.reduce(
        (acc, t) => acc + (t?.cleaning_slots_needed ?? 0),
        0
    );
    const standbyTrains = fleet.filter((t) => t?.status === "Standby").length;

    return (
        <section className="mb-4 grid grid-cols-1 gap-4 sm:grid-cols-3">
            {/* Total Job Cards */}
            <div className="rounded-xl p-5 shadow bg-indigo-600  
                shadow-none transition-shadow 
                duration-300 cursor-pointer hover:shadow-lg hover:shadow-gray-500  ">
                <p className="text-sm text-white uppercase tracking-wide/relaxed opacity-90 ">
                    Total Job Cards
                </p>
                <p className="mt-1 text-3xl text-white font-semibold">{totalJobs}</p>
            </div>

            {/* Cleaning Needed */}
            <div className="rounded-xl p-5 shadow bg-amber-400 text-slate-900
             shadow-none transition-shadow 
                duration-300 cursor-pointer hover:shadow-lg hover:shadow-gray-500  ">
                <p className="text-sm uppercase tracking-wide/relaxed opacity-90">
                    Cleaning Needed
                </p>
                <p className="mt-1 text-3xl font-semibold">{cleaningNeeded}</p>
            </div>

            {/* Standby Trains */}
            <div className="rounded-xl p-5 shadow bg-emerald-600 text-white
             shadow-none transition-shadow 
                duration-300 cursor-pointer hover:shadow-lg hover:shadow-gray-500  ">
                <p className="text-sm uppercase tracking-wide/relaxed opacity-90">
                    Standby Trains
                </p>
                <p className="mt-1 text-3xl font-semibold">{standbyTrains}</p>
            </div>
        </section>
    );
}