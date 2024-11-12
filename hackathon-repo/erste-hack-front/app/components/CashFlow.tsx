import {Card} from "@geist-ui/react";

interface CashFlowProps {
    income?: number
    expense?: number
    style?: object
}

export default function CashFlow({
                                         income = 500.00,
                                         expense = 99.00,
                                         style = {},
                                     }: CashFlowProps) {
    // Calculate the percentage for the expense progress bar
    const expensePercentage = Math.abs((expense / income) * 100)
    const thisMonth = income - expense

    return (
        <Card style={style} className="w-full">
            <Card.Content className="space-y-2">
                <div className="px-4 space-y-2">
                    <h4 className="font-semibold mb-0">Cash Flow</h4>
                    <div className="space-y-1">
                        <p className="m-0 text-sm text-gray-500 uppercase tracking-wider">THIS MONTH</p>
                        <h4 className="m-0 font-semibold">€ {thisMonth}</h4>
                    </div>

                    <div className="space-y-2">
                        <div className="flex justify-between items-center">
                            <span className="text-sm text-gray-600 uppercase">Income</span>
                            <span className="text-sm font-medium">€ {income}</span>
                        </div>
                        <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
                            <div
                                className="h-full bg-emerald-500 rounded-full"
                                style={{width: '100%'}}
                            />
                        </div>
                    </div>

                    <div className="space-y-2">
                        <div className="flex justify-between items-center">
                            <span className="text-sm text-gray-600">EXPENSE</span>
                            <span
                                className="text-sm font-medium">€ {Math.abs(expense as number)}</span>
                        </div>
                        <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
                            <div
                                className="h-full bg-red-500 rounded-full transition-all duration-300 ease-in-out"
                                style={{width: `${expensePercentage}%`}}
                            />
                        </div>
                    </div>
                </div>
            </Card.Content>
        </Card>
    )
}