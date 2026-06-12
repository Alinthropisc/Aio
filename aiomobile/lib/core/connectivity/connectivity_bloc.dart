import 'dart:async';
import 'package:bloc/bloc.dart';
import 'package:equatable/equatable.dart';
import 'package:injectable/injectable.dart';
import '../network/connectivity_service.dart';

part 'connectivity_event.dart';
part 'connectivity_state.dart';

@injectable
final class ConnectivityBloc
    extends Bloc<ConnectivityEvent, ConnectivityState> {
  final ConnectivityService _service;
  StreamSubscription<bool>? _sub;

  ConnectivityBloc(this._service) : super(const ConnectivityUnknown()) {
    on<ConnectivityStartMonitoring>(_onStart);
    on<ConnectivityStatusChanged>(_onChanged);
  }

  Future<void> _onStart(
    ConnectivityStartMonitoring event,
    Emitter<ConnectivityState> emit,
  ) async {
    final online = await _service.isConnected;
    emit(online ? const ConnectivityOnline() : const ConnectivityOffline());

    _sub ??= _service.onConnectivityChanged.listen(
      (online) => add(ConnectivityStatusChanged(isOnline: online)),
    );
  }

  void _onChanged(
    ConnectivityStatusChanged event,
    Emitter<ConnectivityState> emit,
  ) =>
      emit(
        event.isOnline ? const ConnectivityOnline() : const ConnectivityOffline(),
      );

  @override
  Future<void> close() {
    _sub?.cancel();
    return super.close();
  }
}
