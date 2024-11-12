import {Card, Button} from "@geist-ui/react"
import '../style/style.css';
import CashFlow from "@/app/components/CashFlow";
import BankCardVisual from "@/app/components/BankCardVisual";
import {Search} from "@geist-ui/icons";
import {useEffect, useState} from "react";
import InvestmentChart from "@/app/components/InvestmentChart";
import ExpensePie from "@/app/components/ExpensePie";
import InsightOfTheDayCard from "@/app/components/InsightOfTheDayCard";
import {Loading} from "@geist-ui/core";

interface SpendCategory {
    category_name: string;
    montly_spend: number;
}

interface TopInvestment {
    company_name: string;
    profit_index: number;
    percent_earned_in_the_last_year: number;
    money_earned_last_year: number;
}

interface CardData {
    card_number: string;
    expiration_date: string;
}

interface UserData {
    username: string;
    card_data: CardData;
    monthly_incomes: number;
    stock_income: number;
    monthly_expenses: number;
    spend_categories: SpendCategory[];
    year_investments: number;
    month_investments: number;
    top_investments: TopInvestment[];
    tip_of_the_day: string;
}


const styles = {
    card: {
        backgroundColor: '#1B1932',
        border: 'none',
        borderRadius: '1.5rem',
    },
}

export default function DashboardLayout() {
    const [data, setData] = useState<UserData | null>(null);
    const [cardParts , setCardParts] = useState(null);

    const sampleDataInvestment = [
        { month: "Jan", investment: 1000 },
        { month: "Feb", investment: 1200 },
        { month: "Mar", investment: 1500 },
        { month: "Apr", investment: 1300 },
        { month: "May", investment: 1600 },
        { month: "Jun", investment: 1700 },
        { month: "Jul", investment: 1400 },
        { month: "Aug", investment: 1800 },
        { month: "Sep", investment: 1900 },
        { month: "Oct", investment: 2000 },
        { month: "Nov", investment: 2100 },
    ];

    useEffect(() => {
        fetch('/user-example.json')
            .then((response) => response.json())
            .then((jsonData) => {
                setData(jsonData)
                if (jsonData?.card_data?.card_number) {
                    setCardParts(jsonData.card_data.card_number.split(" "))
                }
            })
            .catch((error) => console.error('Error loading JSON data:', error));
    }, []);

    return (
        <div className="bg-[#0D0B21] text-white p-6 pt-2">
             {/*Header */}
            <div className="flex justify-between items-center mb-8">
                <div>
                    <h1 className="text-2xl font-semibold mb-0">
                        Welcome Back, {data?.username || 'User'}  <span role="img" aria-label="wave">👋</span>
                    </h1>
                    <p className="text-gray-400 mt-0">Here&#39;s what&#39;s happening with your store today.</p>
                </div>
                <Card
                    style={styles.card}
                >
                    <Search/>
                </Card>
            </div>

            {/* Metrics Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
                <BankCardVisual
                    numbers={cardParts ?? []}
                    username={data ? data.username : null}
                    expirationDate={data && data.card_data ? data.card_data.expiration_date : null}
                />

                <CashFlow income={data?.monthly_incomes} expense={data?.monthly_expenses} style={{...styles.card, minWidth: '28rem'}}/>

                {/* Activity Section */}
                <Card style={styles.card} className="card border-0 rounded-2xl">
                    <Card.Content className="min-h-32">
                        <div className="px-4">
                            <h4 className="font-semibold mb-0">Expenses</h4>
                            <ExpensePie/>
                        </div>
                    </Card.Content>
                </Card>
            </div>

            {/* Analytics Section */}
            <div className="grid grid-cols-3 gap-6">
                <div className="col-span-1">
                    <Card style={styles.card} className="card border-0">
                        <Card.Content>
                            <div className="flex items-center justify-between">
                                <h4 className="font-semibold mb-0">Analytics</h4>
                                <div className="flex items-center gap-4">
                                    {/* eslint-disable-next-line @typescript-eslint/ban-ts-comment */}
                                    {/*@ts-expect-error*/}
                                    <Button className="text-sm border-white/10">
                                        2024
                                    </Button>
                                </div>
                            </div>
                        </Card.Content>
                        <Card.Content>
                            <div className="h-[300px] flex items-center justify-center text-gray-500">
                                <Loading style={{fontSize: '1.5rem'}}>Loading</Loading>
                            </div>
                        </Card.Content>
                    </Card>
                </div>

                <div className="col-span-1">
                   <InsightOfTheDayCard product={'cappuccino'} category={'entertainment and rest'} amount={228} percentage={132} averageAmount={54}  onRegenerate={null}/>
                </div>

                <Card style={{...styles.card, display: 'flex', flexDirection: 'column', alignItems: 'center'}} className="card border-0">
                    <Card.Content>
                        <div className="px-4 mb-4 space-y-2">
                            <h4 className="font-semibold mb-0">Investments</h4>
                            <div>
                                <h3 className="m-0 text-lg font-bold">Monthly investments: € {data?.month_investments || 53248}</h3>
                                <h4 className="text-base text-gray-500">Yearly investments: € {data?.year_investments || 255426}</h4>
                            </div>
                            <div className="h-64">
                                <InvestmentChart data={sampleDataInvestment}/>
                            </div>
                        </div>
                    </Card.Content>
                </Card>

            </div>
        </div>
    )
}