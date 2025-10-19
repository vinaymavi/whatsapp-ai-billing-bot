import './App.css'
import Header from './components/Header/Header'
import { Outlet} from 'react-router'
function App() {
  return (
    <div className='flex flex-col items-center justify-center'>
      <Header />
      <Outlet/>
    </div>
  )
}

export default App
