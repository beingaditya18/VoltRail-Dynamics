import {
    Chart as ChartJS,
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    Title,
    Tooltip,
    Legend,
} from "chart.js";
import { Line } from "react-chartjs-2";

ChartJS.register(
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    Title,
    Tooltip,
    Legend
);

const options = {
    responsive: true,
    plugins: {
        legend: {
            position: "top",
            align: "center",
            labels: {
                boxWidth: 30,
            },
        },
        title: { display: false },
    },
    scales: {
        y: {
            min: 0,
            max: 1,
            ticks: { stepSize: 0.1 },
            grid: { color: "rgba(0,0,0,0.06)" },
        },
        x: {
            grid: { display: false },
        },
    },
};

const AverageDelayChart = ({
    labels = ["Jan", "Feb", "Mar", "Apr", "May", "Jun"],
    points = [0.12, 0.35, 0.28, 0.55, 0.42, 0.39],
    // labels = [""],
    // points = [0.12, 0.35, 0.28, 0.55, 0.42, 0.39],
}) => {
    const data = {
        labels,
        datasets: [
            {
                label: "Average Delay (min)",
                data: points,
                borderColor: "#e74c3c",
                backgroundColor: "rgba(231, 76, 60, 0.2)",
                fill: false,
                tension: 0.35,
                pointRadius: 0,
            },
        ],
    };

    return <Line options={options} data={data} />;
};

export default AverageDelayChart;