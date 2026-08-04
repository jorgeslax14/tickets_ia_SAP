import { render, screen } from '@testing-library/react';
import App from './App';

test('renders login page by default', () => {
  render(<App />);
  const titleElement = screen.getByText(/Ingresa para ver el dashboard de tickets/i);
  expect(titleElement).toBeInTheDocument();
});
