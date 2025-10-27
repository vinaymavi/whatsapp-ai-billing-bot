import { render, screen, fireEvent, createEvent } from '@testing-library/react';
import { BrowserRouter } from 'react-router';
import { vi } from 'vitest';
import { LoginForm } from './LoginForm';

const renderLoginForm = (props: any) => {
  return render(
    <BrowserRouter>
      <LoginForm {...props} />
    </BrowserRouter>
  );
};

describe('LoginForm', () => {
  it('renders the title, description, input placeholder, and button label correctly', () => {
    const props = {
      title: 'Welcome',
      desc: 'Please enter your mobile number',
      inputPlaceholder: 'Mobile Number',
      buttonLabel: 'Login',
    };

    renderLoginForm(props);

    expect(screen.getByText('Welcome')).toBeInTheDocument();
    expect(screen.getByText('Please enter your mobile number')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('Mobile Number')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Login' })).toBeInTheDocument();
  });

  it('prevents default form submission', () => {
    const props = {
      title: 'Test',
      desc: 'Test desc',
      inputPlaceholder: 'Test placeholder',
      buttonLabel: 'Test button',
    };

    renderLoginForm(props);

    const form = screen.getByRole('form');

    const preventDefault = vi.fn();
    const mockEvent = createEvent.submit(form);
    mockEvent.preventDefault = preventDefault;
    fireEvent(form, mockEvent);

    expect(mockEvent.preventDefault).toHaveBeenCalled();
  });

  it('renders the input with correct attributes', () => {
    const props = {
      title: 'Test',
      desc: 'Test desc',
      inputPlaceholder: 'Enter text',
      buttonLabel: 'Submit',
    };

    renderLoginForm(props);

    const input = screen.getByPlaceholderText('Enter text');
    // component uses type="tel" for phone number input
    expect(input).toHaveAttribute('type', 'tel');
    expect(input).toHaveAttribute('id', 'mobile-num');
  });
});
