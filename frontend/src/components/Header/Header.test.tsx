import { render, screen } from '@testing-library/react';
import Header from './Header';

test('renders Header component', () => {
	render(<Header title="Chat bot admin login" />);
	const linkElement = screen.getByText(/Chat bot admin login/i);
	expect(linkElement).toBeInTheDocument();
});