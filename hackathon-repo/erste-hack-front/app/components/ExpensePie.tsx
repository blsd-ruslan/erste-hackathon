import {Cell, Pie, PieChart, ResponsiveContainer} from "recharts";

const data = [
    { name: 'Food & Restaurant', value: 400 },
    { name: 'Rental', value: 300 },
    { name: 'Electronics', value: 300 },
];

const COLORS = ['#CF63E6', '#10B981', '#E6C163'];

const RADIAN = Math.PI / 180;
// eslint-disable-next-line @typescript-eslint/ban-ts-comment
//@ts-expect-error
const renderCustomizedLabel = ({ cx, cy, midAngle, innerRadius, outerRadius, percent, index }) => {
    const radius = innerRadius + (outerRadius - innerRadius) * 1.2;
    const x = cx + radius * Math.cos(-midAngle * RADIAN);
    const y = cy + radius * Math.sin(-midAngle * RADIAN);

    return (
        <text x={x} y={y} fill="white" textAnchor={x > cx ? 'start' : 'end'} dominantBaseline="central">
            {`${data[index].name} ${(percent * 100).toFixed(0)}%`}
        </text>
    );
};

const ExpensePie = () => {
    return (
        <ResponsiveContainer width="100%" height="100%" className="min-h-48">
            <PieChart width={350} height={350}>
                <Pie
                    data={data}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={renderCustomizedLabel}
                    outerRadius={65}
                    fill="#8884d8"
                    dataKey="value"
                >
                    {data.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                </Pie>
            </PieChart>
        </ResponsiveContainer>
    );
}

export default ExpensePie;