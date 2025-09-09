export const dynamic = 'force-dynamic';
export const runtime = 'nodejs';

export async function GET() {
  return new Response('ok', { status: 200, headers: { 'content-type': 'text/plain; charset=utf-8' } });
}

export async function HEAD() {
  return new Response(null, { status: 200 });
}
