export interface Env {
  DB: D1Database;
  ASSETS: Fetcher;
}

interface EventRecord {
  id?: number;
  person: string;
  timestamp: string;
  content: string;
  anger: number;
}

function calcAnger(content: string): number {
  if (!content) return 1;
  const exclam = (content.match(/!/g) || []).length;
  const length = content.length;
  return Math.min(5, 1 + exclam + Math.floor(length / 50));
}

function jsonResponse(data: unknown, init: ResponseInit = {}): Response {
  const headers = { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*', 'Access-Control-Allow-Methods': 'GET,POST,OPTIONS', 'Access-Control-Allow-Headers': 'Content-Type', ...init.headers };
  return new Response(JSON.stringify(data), { ...init, headers });
}

export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const url = new URL(request.url);

    if (request.method === 'OPTIONS') {
      return new Response(null, {
        status: 204,
        headers: {
          'Access-Control-Allow-Origin': '*',
          'Access-Control-Allow-Methods': 'GET,POST,OPTIONS',
          'Access-Control-Allow-Headers': 'Content-Type',
        },
      });
    }

    if (url.pathname === '/events' && request.method === 'POST') {
      const data = await request.json();
      const person = data.person;
      const content = data.content;
      const timestamp = data.timestamp || new Date().toISOString();
      const anger = calcAnger(content);
      await env.DB.prepare(
        'INSERT INTO events (person, timestamp, content, anger) VALUES (?1, ?2, ?3, ?4)'
      )
        .bind(person, timestamp, content, anger)
        .run();
      return jsonResponse({ status: 'ok', anger });
    }

    if (url.pathname === '/events' && request.method === 'GET') {
      const { results } = await env.DB.prepare(
        'SELECT id, person, timestamp, content, anger FROM events ORDER BY timestamp DESC'
      ).all();
      return jsonResponse(results);
    }

    if (url.pathname === '/summary') {
      const date = url.searchParams.get('date');
      let query = 'SELECT anger FROM events';
      const params: unknown[] = [];
      if (date) {
        query += ' WHERE timestamp BETWEEN ?1 AND ?2';
        params.push(`${date} 00:00:00`, `${date} 23:59:59`);
      }
      const { results } = await env.DB.prepare(query).bind(...params).all();
      const total = results.reduce((sum: number, r: any) => sum + r.anger, 0);
      return jsonResponse({ total_anger: total, count: results.length });
    }

    if (url.pathname === '/scores') {
      const { results } = await env.DB.prepare(
        'SELECT person, SUM(anger) as total FROM events GROUP BY person ORDER BY total DESC'
      ).all();
      const scores = results.map((row: any) => {
        let grade = 'Petty';
        if (row.total >= 20) grade = 'Arch Nemesis';
        else if (row.total >= 10) grade = 'Enemy';
        else if (row.total >= 5) grade = 'Annoying';
        return { person: row.person, score: row.total, grade };
      });
      return jsonResponse(scores);
    }

    if (url.pathname === '/filter') {
      const start = url.searchParams.get('start');
      const end = url.searchParams.get('end');
      const level = url.searchParams.get('level');
      const params: unknown[] = [];
      let q = 'SELECT person, anger FROM events WHERE 1=1';
      if (start) {
        q += ' AND timestamp >= ?' + (params.length + 1);
        params.push(start);
      }
      if (end) {
        q += ' AND timestamp <= ?' + (params.length + 1);
        params.push(end);
      }
      if (level) {
        q += ' AND anger = ?' + (params.length + 1);
        params.push(Number(level));
      }
      const { results } = await env.DB.prepare(q).bind(...params).all();
      return jsonResponse(results.map((r: any) => ({ person: r.person, anger: r.anger })));
    }

    return env.ASSETS.fetch(request);
  },
};
