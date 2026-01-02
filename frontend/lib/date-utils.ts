import { formatDistanceToNow, format } from 'date-fns';
import { fr } from 'date-fns/locale';

export const formatRelativeDate = (date: string) => {
  return formatDistanceToNow(new Date(date), {
    addSuffix: true,
    locale: fr,
  });
};

export const formatDate = (date: string) => {
  return format(new Date(date), 'dd MMM yyyy', { locale: fr });
};
