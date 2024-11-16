export default function () {
  ElNotification({
    title: 'Server Fehler',
    type: 'error',
    message: 'Versuchen Sie es später erneut oder fragen Sie den Administrator'
  });
}