import { render, screen, fireEvent, createEvent } from '@testing-library/react';
import { vi } from 'vitest';
import { LoginForm } from './LoginForm';

describe('LoginForm', () => {
  it('renders the title, description, input placeholder, and button label correctly', () => {
    const props = {
      title: 'Welcome',
      desc: 'Please enter your mobile number',
      inputPlaceholder: 'Mobile Number',
      buttonLabel: 'Login',
    };

    render(<LoginForm {...props} />);

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

    render(<LoginForm {...props} />);

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

    render(<LoginForm {...props} />);

    const input = screen.getByPlaceholderText('Enter text');
    expect(input).toHaveAttribute('type', 'text');
    expect(input).toHaveAttribute('id', 'mobile-num');
  });
});