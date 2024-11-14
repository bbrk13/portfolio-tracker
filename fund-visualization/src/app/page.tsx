import { PortfolioTable } from '@/components/portfolio/PortfolioTable';
import { FundChart } from '@/components/fund/FundChart';

export default function Home() {
  return (
    <div className="grid grid-cols-1 gap-8">
      <section className="bg-white rounded-lg shadow p-6">
        <h2 className="text-2xl font-bold mb-4">Portfolio Summary</h2>
        <PortfolioTable />
      </section>

      <section className="bg-white rounded-lg shadow p-6">
        <h2 className="text-2xl font-bold mb-4">Recent Performance</h2>
        <FundChart />
      </section>
    </div>
  );
} 