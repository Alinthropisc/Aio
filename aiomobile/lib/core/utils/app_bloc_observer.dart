import 'package:bloc/bloc.dart';
import 'package:logger/logger.dart';

final class AppBlocObserver extends BlocObserver {
  final _log = Logger();

  @override
  void onError(BlocBase<dynamic> bloc, Object error, StackTrace stackTrace) {
    _log.e('[${bloc.runtimeType}]', error: error, stackTrace: stackTrace);
    super.onError(bloc, error, stackTrace);
  }

  @override
  void onChange(BlocBase<dynamic> bloc, Change<dynamic> change) {
    super.onChange(bloc, change);
    _log.d('[${bloc.runtimeType}] ${change.currentState} → ${change.nextState}');
  }
}
