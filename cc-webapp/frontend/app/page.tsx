
import App from './App';
import { cookies } from 'next/headers';

export default async function Home() {
  const c = await cookies();
  const token = c.get('auth_token')?.value;
  if (!token) {
    return (
      <>
        <noscript>
          <meta httpEquiv="refresh" content="0;url=/login" />
        </noscript>
        <script dangerouslySetInnerHTML={{ __html: "location.replace('/login');" }} />
      </>
    );
  }
  return <App isAuthenticated={true} />;
}
