import './App.css'
import Header from './components/Header/Header'
import { LoginForm } from './components/LoginForm/LoginForm'

function App() {
  return (
    <div className='flex flex-col items-center justify-center'>
      <Header title='Chat bot admin login' />
      <LoginForm  title='Welcome to admin' desc='Sign in to manage your batch job runs.' buttonLabel='WhatsApp OTP' inputPlaceholder='Admin mobile #'/>
    </div>
  )
}

export default App
