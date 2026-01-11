import { GetServerSideProps } from 'next';

// 301 Redirect: /documents/ibb-plan-notlari → /documents/izmir-buyuksehir-plan-notlari
// SEO için kalıcı yönlendirme - eski URL artık geçersiz

export const getServerSideProps: GetServerSideProps = async () => {
  return {
    redirect: {
      destination: '/documents/izmir-buyuksehir-plan-notlari/',
      permanent: true, // 301 redirect
    },
  };
};

export default function IbbPlanNotlariRedirect() {
  return null;
}
