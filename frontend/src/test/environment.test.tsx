import { useState } from 'react';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, expect, it } from 'vitest';

function Probe() {
  const [count, setCount] = useState(0);
  return <button onClick={() => setCount(count + 1)}>확인 횟수 {count}</button>;
}

describe('DOM test environment', () => {
  it('runs a React interaction using user-event and jest-dom assertions', async () => {
    const user = userEvent.setup();
    render(<Probe />);
    await user.click(screen.getByRole('button', { name: '확인 횟수 0' }));
    expect(screen.getByRole('button')).toHaveAccessibleName('확인 횟수 1');
  });

  it('cleans the previous DOM and starts with independent component state', () => {
    render(<Probe />);
    expect(screen.getAllByRole('button')).toHaveLength(1);
    expect(screen.getByRole('button')).toHaveAccessibleName('확인 횟수 0');
  });
});
