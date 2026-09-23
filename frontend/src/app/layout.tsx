import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'NutriDeals - Comparateur de Compléments Alimentaires & Score Protéique',
  description: 'Trouvez les meilleures offres de Whey et compléments alimentaires en France au meilleur prix par kg avec analyse du Score Protéique.',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="fr">
      <body className="bg-[#0B0F17] text-gray-100 antialiased">{children}</body>
    </html>
  );
}
