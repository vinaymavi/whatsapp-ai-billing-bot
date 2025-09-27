import { render, screen } from '@testing-library/react';
import Header from './Header';

test('renders Header component', () => {
	render(<Header />);
	const linkElement = screen.getByText(/Chat bot admin login/i);
	expect(linkElement).toBeInTheDocument();
});