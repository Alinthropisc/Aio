import 'package:bloc_test/bloc_test.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';

import 'package:aiomobile/core/error/failures.dart';
import 'package:aiomobile/features/auth/domain/entities/user.dart';
import 'package:aiomobile/features/auth/domain/usecases/login_usecase.dart';
import 'package:aiomobile/features/auth/presentation/bloc/auth_bloc.dart';

class MockLoginUseCase extends Mock implements LoginUseCase {}

void main() {
  late MockLoginUseCase loginUseCase;
  late AuthBloc bloc;

  const tUser = User(id: '1', email: 'test@aio.dev');
  const tToken = 'access.token.here';
  const tParams = LoginParams(email: 'test@aio.dev', password: 'password123');

  setUpAll(() {
    registerFallbackValue(tParams);
  });

  setUp(() {
    loginUseCase = MockLoginUseCase();
    bloc = AuthBloc(loginUseCase: loginUseCase);
  });

  tearDown(() => bloc.close());

  test('initial state is AuthInitial', () {
    expect(bloc.state, const AuthInitial());
  });

  group('AuthLoginRequested', () {
    blocTest<AuthBloc, AuthState>(
      'emits [AuthLoading, AuthAuthenticated] on success',
      build: () {
        when(() => loginUseCase(any())).thenAnswer(
          (_) async => (data: (user: tUser, accessToken: tToken), failure: null),
        );
        return bloc;
      },
      act: (b) => b.add(
        AuthLoginRequested(email: tParams.email, password: tParams.password),
      ),
      expect: () => [const AuthLoading(), const AuthAuthenticated(tUser)],
    );

    blocTest<AuthBloc, AuthState>(
      'emits [AuthLoading, AuthFailureState] on server failure',
      build: () {
        when(() => loginUseCase(any())).thenAnswer(
          (_) async => (
            data: null,
            failure: const ServerFailure('Invalid credentials', statusCode: 401),
          ),
        );
        return bloc;
      },
      act: (b) => b.add(
        AuthLoginRequested(email: tParams.email, password: tParams.password),
      ),
      expect: () => [
        const AuthLoading(),
        const AuthFailureState('Invalid credentials'),
      ],
    );

    blocTest<AuthBloc, AuthState>(
      'emits [AuthLoading, AuthFailureState] on network failure',
      build: () {
        when(() => loginUseCase(any())).thenAnswer(
          (_) async => (
            data: null,
            failure: const NetworkFailure('No internet connection'),
          ),
        );
        return bloc;
      },
      act: (b) => b.add(
        AuthLoginRequested(email: tParams.email, password: tParams.password),
      ),
      expect: () => [
        const AuthLoading(),
        const AuthFailureState('No internet connection'),
      ],
    );
  });

  group('AuthLogoutRequested', () {
    blocTest<AuthBloc, AuthState>(
      'emits [AuthUnauthenticated] on logout',
      build: () => bloc,
      act: (b) => b.add(AuthLogoutRequested()),
      expect: () => [const AuthUnauthenticated()],
    );
  });
}
