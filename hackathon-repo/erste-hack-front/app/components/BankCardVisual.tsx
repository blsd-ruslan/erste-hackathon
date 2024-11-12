import '../style/card.css';
import Image from "next/image";

interface BankCardVisualProps {
    numbers: string[]; // array of strings representing the card numbers
    username: string | null; // username or null if not provided
    expirationDate: string | null; // expiration date or null if not provided
}

const styles = {
    card: {
        border: 'none',
        borderRadius: '1.5rem',
    },
};

export default function BankCardVisual({ numbers, username, expirationDate }: BankCardVisualProps) {
    return (
        <div style={styles.card} className="credit-card">
            <div className="head">
                <Image
                    style={{ marginLeft: "-2rem" }}
                    src="/Logo_Erste_Bank_2023.svg"
                    alt="Erste logo"
                    width="150"
                    height="64"
                />
                <div>Virtual Credit Card</div>
            </div>

            <div className="number">
                {numbers && numbers.map((num, index) => (
                    <div key={index}>{num}</div>
                ))}
            </div>

            <div className="tail">
                {username && (
                    <div style={{ fontSize: "1.3rem" }}>{username}</div>
                )}
                {expirationDate && (
                    <div className="exp">
                        <span className="exp-date">{expirationDate}</span>
                    </div>
                )}
            </div>
        </div>
    );
}
