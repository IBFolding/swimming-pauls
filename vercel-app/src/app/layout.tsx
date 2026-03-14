import './globals.css';
import WalletContextProvider from '@/components/WalletContextProvider';

export const metadata = {
  title: 'Swimming Pauls 🐟',
  description: 'When MiroFish is too hard, ask Paul. And his multiples.',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <WalletContextProvider>{children}</WalletContextProvider>
      </body>
    </html>
  );
}