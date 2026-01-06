import React, { useEffect, useState } from 'react';
import { Routes, Route } from 'react-router-dom';
import AppNavbar from './components/AppNavbar'
import AverageDelayChart from './pages/AverageDelayChart'
import FleetTable from './pages/FleetTable';
// import MaintenanceCards from './pages/MaintenanceCards';
import ScheduleCalendar from './pages/ScheduleCalendar';
import { fetchFleet, fetchOptimizedAssignments } from './api';
import MaintenanceCards from './pages/MaintenanceCards';

function App() {
  const [fleet, setFleet] = useState([]);
  const [assignments, setAssignments] = useState([]);
  const [objective, setObjective] = useState(0);

  // useEffect(() => {
  //   fetchFleet().then(setFleet)
  //     .catch(console.error);
  //   fetchOptimizedAssignments()
  //     .then(() => {
  //       setAssignments(res.objective);
  //       setObjective(res.objective.toFixed(2))
  //     })
  //     .catch(console.error)
  // })

  useEffect(() => {
    fetchFleet()
      .then(setFleet)
      .catch(console.error);
    fetchOptimizedAssignments()
      .then(res => {
        setAssignments(res.assignments);
        setObjective(res.objective);
      })
      .catch(console.error);
  }, []);

  // return (
  //   <>
  //     <AppNavbar objective={objective} />
  //     <Routes>

  //       <div>

  //         <Route path="/" element={<MaintenanceCards />} >
  //           {/* <div className="py-5 pb-5  " style={{ width: "100%", maxWidth: 900, margin: "0 auto" }} >
  //             <MaintenanceCards />
  //           </div> */}
  //         </Route>

  //         <Route>
  //           {/* <div className='mt-5'
  //             style={{ width: "100%", maxWidth: 900, margin: "0 auto" }}>

  //             <AverageDelayChart fleet={fleet} />

  //           </div> */}

  //           {/* <div className='pt-8 '
  //             style={{ width: "100%", maxWidth: 900, margin: "0 auto" }}>

  //             <ScheduleCalendar assignments={assignments} />

  //           </div> */}
  //         </Route>
  //         <Route>
  //           {/* <h2 className="mb-2 ml-4 mt-4 text-xl font-semibold text-gray-800">
  //             Fleet Overview
  //           </h2>
  //           <FleetTable fleet={fleet} /> */}
  //         </Route>
  //         <Route>
  //           {/* <h2 className="mb-2 ml-4 mt-4 text-xl font-semibold text-gray-800">
  //             AI Optimized Assignments
  //           </h2>
  //           <FleetTable fleet={fleet} /> */}
  //         </Route>
  //       </div>

  //     </Routes>
  //   </>
  // )

  return (
    <>
      <AppNavbar objective={objective} />
      <div className="py-5 pb-1" style={{ width: "95%", maxWidth: 900, margin: "0 auto" }} >
        <MaintenanceCards />
      </div>

      <Routes>
        {/* <Route path="/maintenanceCards" element={
          <div className="py-5 pb-5" style={{ width: "100%", maxWidth: 900, margin: "0 auto" }} >
            <MaintenanceCards />
          </div>
        } /> */}
        <Route path="/charts" element={
          <>
            <div className='mt-5' style={{ width: "100%", maxWidth: 900, margin: "0 auto" }}>
              <AverageDelayChart fleet={fleet} />
            </div>
            <div className='pt-8' style={{ width: "100%", maxWidth: 900, margin: "0 auto" }}>
              <ScheduleCalendar assignments={assignments} />
            </div>
          </>
        } />

        <Route path="/assignments" element={
          <>
            <h2 className="mb-2 ml-4 mt-4 text-xl font-semibold text-gray-800 hover:italic">
              AI Optimized Assignments
            </h2>
            <div className="m-2  shadow-none transition-shadow 
                duration-300 cursor-pointer hover:shadow-lg hover:shadow-gray-500   ">
              <FleetTable fleet={fleet} />
            </div>
          </>
        } />

        <Route index element={
          < >
            <h2 className="m-2 ml-4 mt-4 text-xl font-semibold text-gray-800 hover:italic">
              Fleet Overview
            </h2>
            <div className="m-2  shadow-none transition-shadow 
                duration-300 cursor-pointer hover:shadow-lg hover:shadow-gray-500   ">
              <FleetTable fleet={fleet} />
            </div>
          </>
        } />
      </Routes>
    </>
  );

}

export default App;
