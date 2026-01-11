// Alan kontrol butonları component'i
import React from 'react';
import DikiliKontrolButtonComponent from './DikiliKontrolButtonComponent';

interface AlanKontrolButtonsProps {
  dikiliKontrolSonucu?: any;
  onOpenDikiliKontrol: () => void;
  formData: any;
}

const AlanKontrolButtons: React.FC<AlanKontrolButtonsProps> = ({
  dikiliKontrolSonucu,
  onOpenDikiliKontrol,
  formData
}) => {
  // Hangi arazi vasfı için hangi kontrol butonunun gösterileceğini belirle
  const shouldShowControl = (
    formData.arazi_vasfi === 'Tarla + herhangi bir dikili vasıflı' ||
    formData.arazi_vasfi === 'Dikili vasıflı' ||
    formData.arazi_vasfi === 'Tarla + Zeytinlik' ||
    formData.arazi_vasfi === 'Zeytin ağaçlı + herhangi bir dikili vasıf' ||
    formData.arazi_vasfi === '… Adetli Zeytin Ağacı bulunan tarla' ||
    formData.arazi_vasfi === '… Adetli Zeytin Ağacı bulunan + herhangi bir dikili vasıf'
  );

  if (!shouldShowControl) return null;

  return (
    <DikiliKontrolButtonComponent
      araziVasfi={formData.arazi_vasfi}
      calculationType="bag-evi"
      dikiliKontrolSonucu={dikiliKontrolSonucu}
      onOpenControl={onOpenDikiliKontrol}
    />
  );
};

export default AlanKontrolButtons;
