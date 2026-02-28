import { useSearchParams } from 'react-router-dom';
import CameraList from '@components/cameras/CameraList';
import CameraForm from '@components/cameras/CameraForm';
import ONVIFDiscovery from '@components/cameras/ONVIFDiscovery';

const Cameras = () => {
  const [searchParams] = useSearchParams();
  const view = searchParams.get('view') || 'list';

  if (view === 'new') {
    return <CameraForm />;
  }

  if (view === 'edit') {
    const cameraId = searchParams.get('camera');
    return <CameraForm />;
  }

  if (view === 'discover') {
    return <ONVIFDiscovery />;
  }

  return <CameraList />;
};

export default Cameras;
