import { useState } from 'react';
import { ArrowUp, ArrowDown, ArrowLeft, ArrowRight, Plus, Minus, RotateCw } from 'lucide-react';
import { PTZ_DIRECTIONS } from '@utils/constants';

const StreamControls = ({ cameraId, onPTZMove, onPTZStop, onPTZGotoPreset, presets = [] }) => {
  const [speed, setSpeed] = useState(1);
  const [isMoving, setIsMoving] = useState(false);

  const handleMoveStart = (direction) => {
    setIsMoving(true);
    if (onPTZMove) {
      onPTZMove(direction, speed);
    }
  };

  const handleMoveStop = () => {
    setIsMoving(false);
    if (onPTZStop) {
      onPTZStop();
    }
  };

  const handleZoomIn = () => {
    if (onPTZMove) {
      onPTZMove(PTZ_DIRECTIONS.ZOOM_IN, speed);
    }
  };

  const handleZoomOut = () => {
    if (onPTZMove) {
      onPTZMove(PTZ_DIRECTIONS.ZOOM_OUT, speed);
    }
  };

  const handleGotoPreset = (presetId) => {
    if (onPTZGotoPreset) {
      onPTZGotoPreset(presetId);
    }
  };

  return (
    <div className="bg-gray-800 rounded-lg p-4 space-y-4">
      {/* Скорость */}
      <div className="flex items-center justify-between">
        <span className="text-white text-sm font-medium">Скорость</span>
        <div className="flex items-center space-x-2">
          <button
            onClick={() => setSpeed(Math.max(1, speed - 1))}
            className="p-1 text-white hover:bg-gray-700 rounded transition-colors"
          >
            <Minus className="w-4 h-4" />
          </button>
          <span className="text-white w-8 text-center">{speed}</span>
          <button
            onClick={() => setSpeed(Math.min(10, speed + 1))}
            className="p-1 text-white hover:bg-gray-700 rounded transition-colors"
          >
            <Plus className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* PTZ управление */}
      <div className="grid grid-cols-3 gap-2">
        <div></div>
        <button
          onMouseDown={() => handleMoveStart(PTZ_DIRECTIONS.UP)}
          onMouseUp={handleMoveStop}
          onMouseLeave={handleMoveStop}
          onTouchStart={() => handleMoveStart(PTZ_DIRECTIONS.UP)}
          onTouchEnd={handleMoveStop}
          className={`p-3 bg-gray-700 hover:bg-gray-600 text-white rounded-lg transition-colors ${
            isMoving ? 'bg-gray-600' : ''
          }`}
        >
          <ArrowUp className="w-5 h-5" />
        </button>
        <div></div>

        <button
          onMouseDown={() => handleMoveStart(PTZ_DIRECTIONS.LEFT)}
          onMouseUp={handleMoveStop}
          onMouseLeave={handleMoveStop}
          onTouchStart={() => handleMoveStart(PTZ_DIRECTIONS.LEFT)}
          onTouchEnd={handleMoveStop}
          className={`p-3 bg-gray-700 hover:bg-gray-600 text-white rounded-lg transition-colors ${
            isMoving ? 'bg-gray-600' : ''
          }`}
        >
          <ArrowLeft className="w-5 h-5" />
        </button>
        <button
          onClick={handleMoveStop}
          className="p-3 bg-gray-700 hover:bg-gray-600 text-white rounded-lg transition-colors"
        >
          <RotateCw className="w-5 h-5" />
        </button>
        <button
          onMouseDown={() => handleMoveStart(PTZ_DIRECTIONS.RIGHT)}
          onMouseUp={handleMoveStop}
          onMouseLeave={handleMoveStop}
          onTouchStart={() => handleMoveStart(PTZ_DIRECTIONS.RIGHT)}
          onTouchEnd={handleMoveStop}
          className={`p-3 bg-gray-700 hover:bg-gray-600 text-white rounded-lg transition-colors ${
            isMoving ? 'bg-gray-600' : ''
          }`}
        >
          <ArrowRight className="w-5 h-5" />
        </button>

        <div></div>
        <button
          onMouseDown={() => handleMoveStart(PTZ_DIRECTIONS.DOWN)}
          onMouseUp={handleMoveStop}
          onMouseLeave={handleMoveStop}
          onTouchStart={() => handleMoveStart(PTZ_DIRECTIONS.DOWN)}
          onTouchEnd={handleMoveStop}
          className={`p-3 bg-gray-700 hover:bg-gray-600 text-white rounded-lg transition-colors ${
            isMoving ? 'bg-gray-600' : ''
          }`}
        >
          <ArrowDown className="w-5 h-5" />
        </button>
        <div></div>
      </div>

      {/* Зум */}
      <div className="flex justify-center space-x-4">
        <button
          onMouseDown={handleZoomIn}
          onMouseUp={handleMoveStop}
          className="flex-1 p-3 bg-gray-700 hover:bg-gray-600 text-white rounded-lg transition-colors"
        >
          <Plus className="w-5 h-5 mx-auto" />
          <span className="text-xs block mt-1">Зум +</span>
        </button>
        <button
          onMouseDown={handleZoomOut}
          onMouseUp={handleMoveStop}
          className="flex-1 p-3 bg-gray-700 hover:bg-gray-600 text-white rounded-lg transition-colors"
        >
          <Minus className="w-5 h-5 mx-auto" />
          <span className="text-xs block mt-1">Зум -</span>
        </button>
      </div>

      {/* Пресеты */}
      {presets.length > 0 && (
        <div>
          <h4 className="text-white text-sm font-medium mb-2">Пресеты</h4>
          <div className="grid grid-cols-2 gap-2">
            {presets.map((preset) => (
              <button
                key={preset.id}
                onClick={() => handleGotoPreset(preset.id)}
                className="p-2 bg-gray-700 hover:bg-gray-600 text-white text-sm rounded-lg transition-colors"
              >
                {preset.name}
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default StreamControls;
