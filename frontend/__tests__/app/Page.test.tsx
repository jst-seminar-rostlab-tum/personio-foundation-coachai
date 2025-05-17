import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import Page from '../../src/app/Page';

const mockMessages = [
  { id: 1, content: 'Hello world!', created_at: '2024-01-01T10:00:00Z' },
  { id: 2, content: 'Testing is great', created_at: '2024-01-02T12:30:00Z' },
];

beforeEach(() => {
  global.fetch = jest.fn();
});

describe('<Page />', () => {
  it('renders loading state initially', async () => {
    (global.fetch as jest.Mock).mockImplementation(() =>
      Promise.resolve({
        json: () => Promise.resolve([]),
      })
    );
    render(<Page />);
    await waitFor(() => {
      expect(screen.getByText('Loading...')).toBeInTheDocument();
    });
  });

  it('renders fetched messages', async () => {
    (global.fetch as jest.Mock).mockResolvedValueOnce({
      json: async () => mockMessages,
    });

    render(<Page />);

    await waitFor(() => {
      expect(screen.getByText('Hello world!')).toBeInTheDocument();
      expect(screen.getByText('Testing is great')).toBeInTheDocument();
    });
  });

  it('allows sending a message', async () => {
    (global.fetch as jest.Mock)
      .mockResolvedValueOnce({ json: async () => mockMessages })
      .mockResolvedValueOnce({
        json: async () => ({
          id: 3,
          content: 'New message!',
          created_at: new Date().toISOString(),
        }),
      });

    render(<Page />);

    await waitFor(() => {
      expect(screen.getByText('Hello world!')).toBeInTheDocument();
    });

    const input = screen.getByPlaceholderText('Type a message...');
    fireEvent.change(input, { target: { value: 'New message!' } });

    const button = screen.getByRole('button', { name: 'Send' });
    fireEvent.click(button);

    await waitFor(() => {
      expect(screen.getByText('New message!')).toBeInTheDocument();
    });
  });

  it('matches snapshot', async () => {
    (global.fetch as jest.Mock).mockResolvedValueOnce({
      json: async () => mockMessages,
    });

    const { asFragment } = render(<Page />);
    await waitFor(() => screen.getByText('Hello world!'));

    expect(asFragment()).toMatchSnapshot();
  });
});
