part of 'connectivity_bloc.dart';

sealed class ConnectivityEvent {}

final class ConnectivityStartMonitoring extends ConnectivityEvent {}

final class ConnectivityStatusChanged extends ConnectivityEvent {
  final bool isOnline;
  ConnectivityStatusChanged({required this.isOnline});
}
