import { ArrowUp, ArrowDown } from 'react-feather';
import { useState, ReactNode } from 'react';

export type EventType = {
  event_id?: string;
  type: string;
  timestamp?: string;
  [key: string]: unknown;
};

type EventProps = {
  event: EventType;
  timestamp?: string;
};

function Event({ event, timestamp }: EventProps) {
  const [isExpanded, setIsExpanded] = useState<boolean>(false);

  const isClient = event.event_id && !event.event_id.startsWith('event_');

  return (
    <div className="flex flex-col gap-2 p-2 rounded-md bg-gray-50">
      <div
        className="flex items-center gap-2 cursor-pointer"
        onClick={() => setIsExpanded(!isExpanded)}
      >
        {isClient ? (
          <ArrowDown className="text-blue-400" />
        ) : (
          <ArrowUp className="text-green-400" />
        )}
        <div className="text-sm text-gray-500">
          {isClient ? 'client:' : 'server:'}
          &nbsp;{event.type} | {timestamp}
        </div>
      </div>
      <div
        className={`text-gray-500 bg-gray-200 p-2 rounded-md overflow-x-auto ${
          isExpanded ? 'block' : 'hidden'
        }`}
      >
        <pre className="text-xs">{JSON.stringify(event, null, 2)}</pre>
      </div>
    </div>
  );
}

type EventLogProps = {
  events: EventType[];
};

export default function EventLog({ events }: EventLogProps) {
  const eventsToDisplay: ReactNode[] = [];
  const deltaEvents: Record<string, EventType> = {};

  events.forEach((event) => {
    if (event.type.endsWith('delta')) {
      if (deltaEvents[event.type]) {
        return;
      }
      deltaEvents[event.type] = event;
    }

    eventsToDisplay.push(<Event key={event.event_id} event={event} timestamp={event.timestamp} />);
  });

  return (
    <div className="flex flex-col gap-2 overflow-x-auto">
      {events.length === 0 ? (
        <div className="text-gray-500">Awaiting events...</div>
      ) : (
        eventsToDisplay
      )}
    </div>
  );
}
