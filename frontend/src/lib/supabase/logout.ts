import { redirect } from 'next/navigation';

// eslint-disable-next-line @typescript-eslint/no-explicit-any
export const logoutUser = async (createClient: any) => {
  const supabase = await createClient();

  const { error } = await supabase.auth.signOut();
  if (error) {
    console.error('Error signing out:', error);
  }

  redirect('/');
};
