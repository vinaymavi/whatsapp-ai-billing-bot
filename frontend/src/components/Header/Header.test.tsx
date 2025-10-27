import { render, screen } from '@testing-library/react';
import Header from './Header';
import { Context } from '@/context/GlobalContext';

test('renders Header component', () => {
	render(
		<Context.Provider value={{ headerTitle: 'Chat bot admin login' }}>
			<Header />
		</Context.Provider>
	);

	const linkElement = screen.getByText(/Chat bot admin login/i);
	expect(linkElement).toBeInTheDocument();
});
