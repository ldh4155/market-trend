import { useEffect, useState } from 'react'
import { fetchSectorList } from '../api'
import SectorTab from '../components/SectorTab'
import CompanyTab from '../components/CompanyTab'

type Tab = 'sector' | 'company'

export default function Home() {
  const [tab, setTab] = useState<Tab>('sector')
  const [sectors, setSectors] = useState<string[]>([])

  useEffect(() => {
    fetchSectorList().then(setSectors).catch(console.error)
  }, [])

  return (
    <div className="app">
      <header>
        <h1>Market Trend</h1>
      </header>

      <div className="tabs">
        <button
          className={tab === 'sector' ? 'active' : ''}
          onClick={() => setTab('sector')}
        >
          섹터 검색
        </button>
        <button
          className={tab === 'company' ? 'active' : ''}
          onClick={() => setTab('company')}
        >
          기업 검색
        </button>
      </div>

      {tab === 'sector' ? (
        <SectorTab sectors={sectors} />
      ) : (
        <CompanyTab sectors={sectors} />
      )}
    </div>
  )
}
